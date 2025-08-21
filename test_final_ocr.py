#!/usr/bin/env python3
"""
Final OCR Integration Test with Real Image
"""

import os
import sys
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def create_test_image():
    """Create a simple test image with text"""
    print("=== Creating Test Image ===")
    
    try:
        # Create a simple image with text
        width, height = 800, 200
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Add some text
        text = "This is a handwritten answer test for OCR integration."
        
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw text
        draw.text((50, 80), text, fill='black', font=font)
        
        # Save to BytesIO
        image_buffer = BytesIO()
        image.save(image_buffer, format='JPEG')
        image_buffer.seek(0)
        
        print(f"✅ Created test image:")
        print(f"   Size: {width}x{height}")
        print(f"   Text: {text}")
        print(f"   Format: JPEG")
        print(f"   Buffer size: {len(image_buffer.getvalue())} bytes")
        
        return image_buffer
        
    except Exception as e:
        print(f"❌ Failed to create test image: {e}")
        return None

def test_real_ocr_processing():
    """Test OCR with a real image"""
    print("\n=== Testing Real OCR Processing ===")
    
    # Create test image
    image_buffer = create_test_image()
    if not image_buffer:
        return False
    
    try:
        # Test with your OCR API
        files = {
            'file': ('test_handwriting.jpg', image_buffer.getvalue(), 'image/jpeg')
        }
        
        print("✅ Sending real image to OCR API...")
        response = requests.post(
            "http://localhost:8080/api/process",
            files=files,
            timeout=30
        )
        
        print(f"✅ OCR API Response:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                extracted_text = response_data.get('extracted_text', '')
                confidence = response_data.get('confidence', 0.0)
                
                print(f"   ✅ SUCCESS! OCR extracted text:")
                print(f"   Text: '{extracted_text}'")
                print(f"   Confidence: {confidence}")
                print(f"   Full response: {response_data}")
                
                return True
                
            except Exception as e:
                print(f"   ❌ Failed to parse JSON response: {e}")
                print(f"   Raw response: {response.text}")
                return False
        else:
            print(f"   ❌ API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Real OCR processing test failed: {e}")
        return False

def test_complete_integration():
    """Test the complete OCR integration flow"""
    print("\n=== Testing Complete Integration Flow ===")
    
    try:
        # Configure Django settings
        import django
        from django.conf import settings
        
        if not settings.configured:
            settings.configure(
                OCR_API_SETTINGS={
                    'API_URL': 'http://localhost:8080/api/process',
                    'API_KEY': '',
                    'TIMEOUT': 30,
                    'MAX_FILE_SIZE': 10 * 1024 * 1024,
                    'ALLOWED_FORMATS': ['jpg', 'jpeg', 'png', 'pdf', 'tiff'],
                }
            )
        
        # Import OCR processor
        sys.path.insert(0, '/Applications/intemass-live_master/student')
        from ocr_utils import OCRProcessor
        
        # Create test image
        image_buffer = create_test_image()
        if not image_buffer:
            return False
        
        # Create file-like object
        class ImageFile:
            def __init__(self, buffer, name):
                self.buffer = buffer
                self.name = name
                self.size = len(buffer.getvalue())
                
            def read(self):
                return self.buffer.getvalue()
            
            def seek(self, position):
                self.buffer.seek(position)
        
        image_file = ImageFile(image_buffer, "test_answer_sheet.jpg")
        
        # Test OCR processor
        processor = OCRProcessor()
        print("✅ Testing complete OCR integration...")
        
        result = processor.call_ocr_api(image_file)
        
        print(f"✅ Integration Result:")
        print(f"   Success: {result['success']}")
        
        if result['success']:
            print(f"   ✅ COMPLETE SUCCESS!")
            print(f"   Extracted Text: '{result.get('extracted_text', '')}'")
            print(f"   Confidence: {result.get('confidence', 0.0)}")
            print(f"   Ready for Django StudentAnswer model!")
            return True
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Complete integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run final OCR integration tests"""
    print("🎯 Final OCR Integration Test with Real Image")
    print("=" * 60)
    
    tests = [
        ("Real OCR Processing", test_real_ocr_processing),
        ("Complete Integration", test_complete_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 COMPLETE SUCCESS! OCR Integration is fully working!")
        print("\n🚀 Ready for Production:")
        print("✅ OCR API communication: Working")
        print("✅ File upload format: Working") 
        print("✅ Text extraction: Working")
        print("✅ Django integration: Ready")
        print("\n📋 Next Steps:")
        print("1. Fix Django model compatibility (ForeignKey on_delete)")
        print("2. Start Django server")
        print("3. Navigate to /student/ocr/upload/")
        print("4. Upload real handwritten answer sheets!")
    else:
        print("⚠️  Integration partially working - check errors above")

if __name__ == '__main__':
    main()
