#!/usr/bin/env python3
"""
OCR API Configuration Script
Run this script to configure your OCR API details
"""

import os
import sys

def configure_ocr_api():
    print("=== OCR API Configuration ===")
    print("This script will help you configure your OCR API integration")
    print()
    
    # Get API details from user
    api_url = input("Enter your OCR API URL (e.g., https://your-ocr-api.com/extract-text): ").strip()
    if not api_url:
        print("Error: API URL is required")
        return False
    
    api_key = input("Enter your API Key (leave empty if no authentication required): ").strip()
    
    timeout = input("Enter API timeout in seconds (default: 30): ").strip()
    if not timeout:
        timeout = "30"
    
    max_file_size = input("Enter max file size in MB (default: 10): ").strip()
    if not max_file_size:
        max_file_size = "10"
    
    # Update settings_local.py
    settings_file = "/Applications/intemass-live_master/settings_local.py"
    
    try:
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Update OCR API settings
        ocr_config = f"""
# OCR API Configuration
OCR_API_SETTINGS = {{
    'API_URL': '{api_url}',
    'API_KEY': '{api_key}',  # Replace with actual API key if needed
    'TIMEOUT': {timeout},  # API timeout in seconds
    'MAX_FILE_SIZE': {max_file_size} * 1024 * 1024,  # {max_file_size}MB max file size
    'ALLOWED_FORMATS': ['jpg', 'jpeg', 'png', 'pdf', 'tiff'],
    'TEMP_UPLOAD_DIR': os.path.join(PROJECTPATH, 'temp_ocr_uploads'),
}}"""
        
        # Replace existing OCR_API_SETTINGS if it exists
        if 'OCR_API_SETTINGS' in content:
            # Find and replace existing config
            import re
            pattern = r'OCR_API_SETTINGS\s*=\s*\{[^}]*\}'
            content = re.sub(pattern, ocr_config.strip(), content, flags=re.DOTALL)
        else:
            # Add after STATICFILES_DIRS
            staticfiles_end = content.find(')')
            if staticfiles_end != -1:
                # Find the end of STATICFILES_DIRS
                staticfiles_end = content.find(')', staticfiles_end) + 1
                content = content[:staticfiles_end] + '\n' + ocr_config + '\n' + content[staticfiles_end:]
        
        # Write updated content
        with open(settings_file, 'w') as f:
            f.write(content)
        
        print("\n✅ OCR API configuration updated successfully!")
        print(f"API URL: {api_url}")
        print(f"API Key: {'***' if api_key else 'Not set'}")
        print(f"Timeout: {timeout} seconds")
        print(f"Max file size: {max_file_size}MB")
        
        return True
        
    except Exception as e:
        print(f"Error updating configuration: {e}")
        return False

def test_ocr_api():
    print("\n=== Testing OCR API Connection ===")
    try:
        import requests
        
        # Load settings
        sys.path.insert(0, '/Applications/intemass-live_master')
        from settings_local import OCR_API_SETTINGS
        
        api_url = OCR_API_SETTINGS.get('API_URL')
        api_key = OCR_API_SETTINGS.get('API_KEY')
        timeout = OCR_API_SETTINGS.get('TIMEOUT', 30)
        
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        print(f"Testing connection to: {api_url}")
        
        # Test with a simple request (you might need to adjust this)
        response = requests.get(api_url.replace('/extract-text', '/health'), 
                              headers=headers, timeout=5)
        
        if response.status_code == 200:
            print("✅ API connection successful!")
        else:
            print(f"⚠️  API responded with status: {response.status_code}")
            
    except ImportError:
        print("❌ requests library not found. Please install: pip3 install requests")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

if __name__ == "__main__":
    if configure_ocr_api():
        test_api = input("\nWould you like to test the API connection? (y/n): ").strip().lower()
        if test_api in ['y', 'yes']:
            test_ocr_api()
    
    print("\nNext steps:")
    print("1. Start the Django development server: python3 manage.py runserver")
    print("2. Navigate to: http://localhost:8000/student/ocr/upload/")
    print("3. Upload a handwritten answer sheet to test the OCR integration")
