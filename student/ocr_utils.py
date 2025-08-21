"""
OCR Integration utilities for processing handwritten answer sheets
"""
import os
import json
import logging
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import base64
from PIL import Image
import io

# Import requests with error handling
try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)

class OCRProcessor:
    """
    Handle OCR API integration for processing handwritten answer sheets
    """
    
    def __init__(self):
        self.api_url = getattr(settings, 'OCR_API_SETTINGS', {}).get('API_URL')
        self.api_key = getattr(settings, 'OCR_API_SETTINGS', {}).get('API_KEY')
        self.timeout = getattr(settings, 'OCR_API_SETTINGS', {}).get('TIMEOUT', 30)
        self.max_file_size = getattr(settings, 'OCR_API_SETTINGS', {}).get('MAX_FILE_SIZE', 10 * 1024 * 1024)
        self.allowed_formats = getattr(settings, 'OCR_API_SETTINGS', {}).get('ALLOWED_FORMATS', ['jpg', 'jpeg', 'png', 'pdf'])
    
    def validate_image(self, image_file):
        """
        Validate uploaded image file
        """
        # Check file size
        if image_file.size > self.max_file_size:
            raise ValueError(f"File size {image_file.size} exceeds maximum allowed size {self.max_file_size}")
        
        # Check file format
        file_extension = image_file.name.split('.')[-1].lower()
        if file_extension not in self.allowed_formats:
            raise ValueError(f"File format '{file_extension}' not supported. Allowed formats: {self.allowed_formats}")
        
        return True
    
    def convert_image_to_base64(self, image_file):
        """
        Convert image file to base64 string for API transmission
        """
        try:
            # Read image content
            image_content = image_file.read()
            
            # Convert to base64
            base64_string = base64.b64encode(image_content).decode('utf-8')
            
            return base64_string
        except Exception as e:
            logger.error(f"Error converting image to base64: {str(e)}")
            raise
    
    def call_ocr_api(self, image_file):
        """
        Call the OCR API with the image file and return extracted text
        """
        try:
            # Check if requests is available
            if requests is None:
                return {
                    'success': False,
                    'error': 'Requests library not available. Please install: pip install requests'
                }
            
            # Check if API URL is configured
            if not self.api_url:
                return {
                    'success': False,
                    'error': 'OCR API URL not configured in settings'
                }
            
            # Validate image
            self.validate_image(image_file)
            
            # Reset file pointer to beginning
            image_file.seek(0)
            
            # Prepare multipart form data for file upload
            files = {
                'file': (image_file.name, image_file.read(), 'application/octet-stream')
            }
            
            # Reset file pointer again for potential reuse
            image_file.seek(0)
            
            # Prepare headers
            headers = {}
            
            # Add authorization header if API key is provided
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Make API request with file upload
            logger.info(f"Calling OCR API: {self.api_url}")
            response = requests.post(
                self.api_url,
                files=files,
                headers=headers,
                timeout=self.timeout
            )
            
            # Check response status
            if response.status_code == 200:
                response_data = response.json()
                extracted_text = response_data.get('extracted_text', '')
                
                logger.info(f"OCR processing successful. Extracted {len(extracted_text)} characters")
                
                return {
                    'success': True,
                    'extracted_text': extracted_text,
                    'confidence': response_data.get('confidence', 0.0),
                    'raw_response': response_data
                }
            else:
                logger.error(f"OCR API error: Status {response.status_code}, Response: {response.text}")
                return {
                    'success': False,
                    'error': f"API returned status {response.status_code}: {response.text}",
                    'raw_response': response.text
                }
                
        except Exception as e:
            # Handle different types of exceptions
            if 'Timeout' in str(type(e)):
                logger.error("OCR API request timeout")
                return {
                    'success': False,
                    'error': 'API request timeout'
                }
            elif 'RequestException' in str(type(e)) or 'ConnectionError' in str(type(e)):
                logger.error(f"OCR API request failed: {str(e)}")
                return {
                    'success': False,
                    'error': f'API request failed: {str(e)}'
                }
            else:
                logger.error(f"OCR processing error: {str(e)}")
                return {
                    'success': False,
                    'error': f'Processing error: {str(e)}'
                }
    
    def process_answer_sheet(self, image_file, student_id, question_id):
        """
        Complete workflow to process an answer sheet image
        """
        try:
            # Call OCR API
            ocr_result = self.call_ocr_api(image_file)
            
            if not ocr_result['success']:
                return ocr_result
            
            # Return processed result
            return {
                'success': True,
                'student_id': student_id,
                'question_id': question_id,
                'extracted_text': ocr_result['extracted_text'],
                'confidence': ocr_result.get('confidence', 0.0),
                'processing_timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Answer sheet processing error: {str(e)}")
            return {
                'success': False,
                'error': f'Answer sheet processing failed: {str(e)}'
            }

# Global OCR processor instance
ocr_processor = OCRProcessor()
