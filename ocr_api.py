#!/usr/bin/env python3
"""
SIMPLE OCR API - Clean JSON output with page-by-page text
Just what you need - no complications!
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import fitz  # PyMuPDF
from PIL import Image
from transformers import VisionEncoderDecoderModel, TrOCRProcessor
import torch
import json
import os

# Initialize FastAPI app
app = FastAPI(
    title="Simple OCR API",
    description="Clean JSON output with page-by-page text extraction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global TrOCR model
trocr_model = None
trocr_processor = None

@app.on_event("startup")
async def startup_event():
    global trocr_model, trocr_processor
    print("🚀 Loading TrOCR model...")
    try:
        trocr_processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
        trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        trocr_model.to(device)
        print(f"✅ TrOCR loaded on {device}")
    except Exception as e:
        print(f"❌ Error loading TrOCR: {e}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Simple OCR API",
        "version": "1.0.0"
    }

@app.post("/api/v1/ocr/upload")
async def upload_and_extract(file: UploadFile = File(...)):
    """
    Upload PDF and extract text using TrOCR
    Returns clean JSON with page-by-page text
    """
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are supported"}
    
    if not trocr_model or not trocr_processor:
        return {"error": "TrOCR model not loaded"}
    
    try:
        # Save uploaded file
        content = await file.read()
        temp_pdf = f"temp_{file.filename}"
        with open(temp_pdf, "wb") as f:
            f.write(content)
        
        # Extract text from PDF
        doc = fitz.open(temp_pdf)
        pages = []
        
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Use TrOCR to extract text
            pixel_values = trocr_processor(images=img, return_tensors="pt").pixel_values
            with torch.no_grad():
                generated_ids = trocr_model.generate(pixel_values)
            text = trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            pages.append({
                "page": page_num + 1,
                "text": text
            })
        
        doc.close()
        
        # Clean up temp file
        os.remove(temp_pdf)
        
        # Return clean JSON response
        return {
            "success": True,
            "filename": file.filename,
            "total_pages": len(pages),
            "pages": pages
        }
        
    except Exception as e:
        return {"error": f"Processing error: {str(e)}"}

if __name__ == "__main__":
    print("🚀 Starting Simple OCR API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📤 Upload Endpoint: http://localhost:8000/api/v1/ocr/upload")
    print("📝 Output: Clean JSON with page-by-page text")
    print("⚡ SIMPLE & CLEAN APPROACH")
    print("⏹️  Press Ctrl+C to stop")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
