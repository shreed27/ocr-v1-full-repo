# Intemass Assessment Platform - OCR Integration

## Overview
This repository contains the complete source code for the **Intemass Assessment Platform** with integrated **Handwritten Answer Sheet OCR** capabilities.

## Quick Start Guide

### 1. Prerequisites
- Python 3.9+
- Django 3.2+
- OCR API service

### 2. Installation
```bash
git clone https://github.com/yourusername/intemass-ocr-platform.git
cd intemass-ocr-platform
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 3. OCR Configuration
Configure your OCR API endpoint in `settings_local.py`:
```python
OCR_API_SETTINGS = {
    'API_URL': 'http://localhost:8080/api/process',
    'TIMEOUT': 30,
    'MAX_FILE_SIZE': 10 * 1024 * 1024,
}
```

### 4. Access Points
- **Main Platform**: `http://localhost:8000/`
- **OCR Upload**: `http://localhost:8000/student/ocr/upload/`
- **Admin Panel**: `http://localhost:8000/admin/`

## Key Features
- ✅ Handwritten text recognition
- ✅ Automatic question-answer mapping
- ✅ Real-time OCR processing
- ✅ Assessment algorithm integration
- ✅ Teacher dashboard
- ✅ Student management
- ✅ Report generation

## Testing
Run the included test files to verify OCR integration:
```bash
python test_real_handwriting.py
python production_status_report.py
```

## Status
🎯 **Production Ready** - Successfully tested with real handwritten answer sheets

## Support
For questions and support, please create an issue in this repository.
