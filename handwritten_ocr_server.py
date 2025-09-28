#!/usr/bin/env python3
"""
Handwritten Answer Sheet OCR Server
Specialized for extracting student handwritten responses from answer sheets
"""

from flask import Flask, request, jsonify
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
import base64
import logging
import traceback
import os
import tempfile
import re
import cv2
import numpy as np

# PDF to image
try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except Exception:
    PDF2IMAGE_AVAILABLE = False

# Import ML libraries globally
try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    import torch
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠️  ML libraries not available: {e}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for model loading
processor = None
model = None
device = None


def initialize_model():
    """Initialize the TrOCR model for handwritten text"""
    global processor, model, device

    if processor is not None:
        return True

    if not ML_AVAILABLE:
        logger.error("ML libraries not available")
        return False

    try:
        print("🔄 Loading Handwritten OCR model...")
        
        # Use base model for better compatibility with handwriting
        processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
        model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        model.eval()

        print(f"✅ Handwritten OCR model loaded on {device}!")
        return True

    except Exception as e:
        logger.error(f"Failed to load TrOCR model: {str(e)}")
        return False


def detect_handwritten_regions(image):
    """Detect handwritten text regions and filter out printed text."""
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Create binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours (potential text regions)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours for handwritten text characteristics
        handwritten_regions = []
        height, width = gray.shape
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter based on size - handwritten text is usually in specific size ranges
            if (w > 20 and h > 10 and w < width * 0.8 and h < height * 0.1):
                # Check if the region contains irregular shapes (characteristic of handwriting)
                aspect_ratio = w / float(h)
                area = cv2.contourArea(contour)
                rect_area = w * h
                extent = float(area) / rect_area
                
                # Handwritten text typically has:
                # - Moderate aspect ratios (not too wide or tall)
                # - Irregular shapes (extent between 0.3-0.8)
                if (0.5 < aspect_ratio < 8.0 and 0.3 < extent < 0.8):
                    handwritten_regions.append((x, y, w, h))
        
        # Sort regions by position (top to bottom, left to right)
        handwritten_regions.sort(key=lambda r: (r[1], r[0]))
        
        return handwritten_regions
    
    except Exception as e:
        logger.warning(f"Handwritten region detection failed: {e}")
        return []


def preprocess_for_handwriting(image: Image.Image) -> Image.Image:
    """Preprocessing specifically optimized for handwritten text recognition."""
    try:
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Ensure good resolution but not too large
        w, h = image.size
        target_size = 2000
        if max(w, h) > target_size:
            scale = target_size / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            image = image.resize((new_w, new_h), Image.LANCZOS)
        elif max(w, h) < 800:
            scale = 800 / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            image = image.resize((new_w, new_h), Image.LANCZOS)

        # Convert to grayscale for better handwriting contrast
        gray_image = ImageOps.grayscale(image)
        
        # Enhance contrast specifically for handwriting
        enhancer = ImageEnhance.Contrast(gray_image)
        gray_image = enhancer.enhance(2.0)  # Strong contrast for handwriting
        
        # Apply slight gaussian blur to smooth pen strokes
        gray_image = gray_image.filter(ImageFilter.GaussianBlur(radius=0.8))
        
        # Convert back to RGB (required by TrOCR)
        image = gray_image.convert('RGB')
        
        # Final sharpening for text clarity
        image = image.filter(ImageFilter.SHARPEN)

        return image
        
    except Exception as e:
        logger.warning(f"Handwriting preprocessing failed: {e}")
        return image


def extract_handwritten_text(image: Image.Image):
    """Extract text specifically from handwritten regions."""
    try:
        if not initialize_model():
            return {"error": "Failed to initialize OCR model"}

        # First, try to detect handwritten regions
        handwritten_regions = detect_handwritten_regions(image)
        
        all_text = []
        
        # Process each detected handwritten region
        if handwritten_regions:
            logger.info(f"Found {len(handwritten_regions)} potential handwritten regions")
            
            for i, (x, y, w, h) in enumerate(handwritten_regions):
                try:
                    # Extract region
                    region = image.crop((x, y, x + w, y + h))
                    
                    # Preprocess region for handwriting
                    processed_region = preprocess_for_handwriting(region)
                    
                    # Extract text from region
                    pixel_values = processor(processed_region, return_tensors="pt").pixel_values.to(device)
                    
                    with torch.no_grad():
                        generated_ids = model.generate(
                            pixel_values,
                            max_length=256,      # Shorter for individual regions
                            min_length=3,        # Minimum meaningful text
                            num_beams=3,         # Moderate beam search
                            do_sample=True,
                            temperature=0.8,     # Allow some variation
                            repetition_penalty=1.5,  # Strong repetition penalty
                            no_repeat_ngram_size=3,
                            pad_token_id=processor.tokenizer.pad_token_id,
                            eos_token_id=processor.tokenizer.eos_token_id
                        )
                        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
                    
                    if text and len(text) > 2:  # Only keep meaningful text
                        all_text.append(text)
                        logger.info(f"Region {i+1}: '{text}'")
                
                except Exception as e:
                    logger.warning(f"Failed to process region {i+1}: {e}")
                    continue
        
        # If no regions detected or no text found, process the whole image
        if not all_text:
            logger.info("Processing full image for handwritten content")
            processed_image = preprocess_for_handwriting(image)
            
            pixel_values = processor(processed_image, return_tensors="pt").pixel_values.to(device)
            
            with torch.no_grad():
                generated_ids = model.generate(
                    pixel_values,
                    max_length=512,
                    min_length=5,
                    num_beams=3,
                    do_sample=True,
                    temperature=0.7,
                    repetition_penalty=1.4,
                    no_repeat_ngram_size=4,
                    pad_token_id=processor.tokenizer.pad_token_id,
                    eos_token_id=processor.tokenizer.eos_token_id
                )
                text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
                
                if text:
                    all_text.append(text)
        
        # Combine all extracted text
        combined_text = ' '.join(all_text)
        
        # Clean the text
        combined_text = clean_handwritten_text(combined_text)
        
        return {
            "data": {
                "raw_extracted_lines": [
                    {"text": combined_text, "conf": 0.85}
                ]
            },
            "text": combined_text,
            "regions_detected": len(handwritten_regions)
        }
        
    except Exception as e:
        logger.error(f"Handwritten text extraction error: {str(e)}")
        return {"error": f"Handwriting extraction failed: {str(e)}"}


def clean_handwritten_text(text: str) -> str:
    """Clean handwritten OCR output."""
    if not text:
        return text
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common OCR artifacts for handwriting
    text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
    
    # Fix common handwriting OCR mistakes
    text = text.replace('|', 'I')
    text = text.replace('0', 'O')  # Context dependent
    text = text.replace('5', 'S')  # Context dependent
    
    return text


def process_pdf_bytes(pdf_bytes: bytes):
    """Process PDF with focus on handwritten content."""
    if not PDF2IMAGE_AVAILABLE:
        return {"error": "pdf2image not available on server"}

    pages = []
    try:
        # Convert with high DPI for handwriting clarity
        images = convert_from_bytes(pdf_bytes, dpi=400)  # Even higher DPI
    except Exception as e:
        logger.error(f"PDF to image conversion failed: {e}")
        return {"error": f"PDF conversion failed: {str(e)}"}

    for idx, img in enumerate(images, start=1):
        try:
            logger.info(f"Processing page {idx}/{len(images)} for handwritten content...")
            
            res = extract_handwritten_text(img)
            
            if "error" in res:
                pages.append({"page": idx, "extracted_text": "", "error": res.get("error")})
            else:
                text = res.get("text", "").strip()
                regions = res.get("regions_detected", 0)
                logger.info(f"Page {idx}: Found {regions} regions, extracted {len(text)} characters")
                pages.append({
                    "page": idx, 
                    "extracted_text": text,
                    "handwritten_regions": regions
                })
                
        except Exception as e:
            logger.error(f"Error processing page {idx}: {str(e)}")
            pages.append({"page": idx, "extracted_text": "", "error": str(e)})

    return {"pages": pages}


@app.route('/api/process', methods=['POST'])
def ocr_process():
    """Handwritten answer sheet OCR endpoint."""
    try:
        files = request.files.getlist('file')
        if not files:
            return jsonify({"error": "No file uploaded"}), 400

        if len(files) == 1:
            file = files[0]
            filename = file.filename or 'upload'
            content = file.read()

            # Check if PDF
            is_pdf = filename.lower().endswith('.pdf') or (len(content) >= 4 and content[:4] == b'%PDF')
            if is_pdf:
                pdf_result = process_pdf_bytes(content)
                if "error" in pdf_result:
                    return jsonify(pdf_result), 500

                pages = pdf_result.get('pages', [])
                return jsonify({
                    "pdf_file": filename,
                    "total_pages": len(pages),
                    "pages": pages,
                    "processing_type": "handwritten_focused"
                }), 200

            # Single image
            try:
                image = Image.open(io.BytesIO(content))
            except Exception as e:
                return jsonify({"error": f"Invalid image file: {str(e)}"}), 400

            result = extract_handwritten_text(image)
            if "error" in result:
                return jsonify(result), 500
            return jsonify(result), 200

        # Multiple files processing would go here...
        return jsonify({"error": "Multiple file processing not implemented"}), 400

    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_status": "loaded" if processor else "not_loaded",
        "service": "Handwritten Answer Sheet OCR",
        "specialization": "Student handwriting recognition"
    })


@app.route('/', methods=['GET'])
def root():
    """Root endpoint info"""
    return jsonify({
        "service": "Handwritten Answer Sheet OCR Server",
        "version": "3.0",
        "specialization": "Student handwritten responses",
        "capabilities": [
            "Handwritten region detection",
            "Printed text filtering", 
            "Handwriting-specific preprocessing",
            "Answer sheet optimization"
        ],
        "status": "running"
    })


if __name__ == '__main__':
    print("🚀 Starting Handwritten Answer Sheet OCR Server...")
    print("📍 Server: http://localhost:8080")
    print("🎯 Specialized for: Student handwritten answers only")
    print("🧠 Features: Handwriting detection + region isolation")
    print()

    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Handwriting OCR Server stopped")
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
