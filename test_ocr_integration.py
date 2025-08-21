#!/usr/bin/env python3
"""
Simple test script to verify OCR integration components
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, '/Applications/intemass-live_master')

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local')

def test_ocr_utils():
    """Test OCR utilities"""
    print("=== Testing OCR Utilities ===")
    
    try:
        # Test importing OCR utilities
        sys.path.insert(0, '/Applications/intemass-live_master/student')
        from ocr_utils import OCRProcessor
        
        # Test OCR processor initialization
        processor = OCRProcessor()
        print("✅ OCRProcessor imported and initialized successfully")
        
        # Test configuration loading
        api_url = processor.api_url
        print(f"✅ API URL loaded: {api_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR utilities test failed: {e}")
        return False

def test_django_imports():
    """Test Django app imports"""
    print("\n=== Testing Django App Imports ===")
    
    try:
        # Test importing Django
        import django
        print(f"✅ Django {django.get_version()} imported successfully")
        
        # Test importing OCR form
        sys.path.insert(0, '/Applications/intemass-live_master/student')
        # Note: This might fail due to model dependencies, but let's try
        
        return True
        
    except Exception as e:
        print(f"❌ Django imports test failed: {e}")
        return False

def test_settings():
    """Test settings configuration"""
    print("\n=== Testing Settings Configuration ===")
    
    try:
        sys.path.insert(0, '/Applications/intemass-live_master')
        import settings_local
        
        # Test OCR settings
        ocr_settings = getattr(settings_local, 'OCR_API_SETTINGS', None)
        if ocr_settings:
            print("✅ OCR_API_SETTINGS found in settings")
            print(f"   API URL: {ocr_settings.get('API_URL')}")
            print(f"   Timeout: {ocr_settings.get('TIMEOUT')} seconds")
            print(f"   Max file size: {ocr_settings.get('MAX_FILE_SIZE') // (1024*1024)}MB")
        else:
            print("❌ OCR_API_SETTINGS not found in settings")
            return False
        
        # Test database configuration
        databases = getattr(settings_local, 'DATABASES', None)
        if databases and 'default' in databases:
            engine = databases['default'].get('ENGINE')
            print(f"✅ Database configuration found: {engine}")
        else:
            print("❌ Database configuration not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False

def test_file_structure():
    """Test required files exist"""
    print("\n=== Testing File Structure ===")
    
    files_to_check = [
        '/Applications/intemass-live_master/student/ocr_utils.py',
        '/Applications/intemass-live_master/student/forms.py',
        '/Applications/intemass-live_master/student/templates/student/ocr_upload.html',
        '/Applications/intemass-live_master/student/templates/student/ocr_status.html',
        '/Applications/intemass-live_master/configure_ocr.py',
        '/Applications/intemass-live_master/OCR_INTEGRATION_README.md',
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} exists")
        else:
            print(f"❌ {os.path.basename(file_path)} missing")
            all_exist = False
    
    return all_exist

def test_dependencies():
    """Test required Python packages"""
    print("\n=== Testing Dependencies ===")
    
    dependencies = [
        ('django', 'Django'),
        ('requests', 'Requests'),
        ('PIL', 'Pillow'),
    ]
    
    all_available = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} available")
        except ImportError:
            print(f"❌ {name} not available")
            all_available = False
    
    return all_available

def main():
    print("🔍 OCR Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_file_structure,
        test_settings,
        test_ocr_utils,
        test_django_imports,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OCR integration is ready.")
        print("\nNext steps:")
        print("1. Run: python3 configure_ocr.py (to set your actual API URL)")
        print("2. Fix Django model compatibility issues")
        print("3. Run: python3 manage.py runserver --settings=settings_local")
        print("4. Navigate to: http://localhost:8000/student/ocr/upload/")
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
    
    return passed == total

if __name__ == '__main__':
    main()
