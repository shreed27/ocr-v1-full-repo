# OCR Integration for Intemass Assessment Platform

## Overview
This integration allows you to upload handwritten answer sheets and automatically extract text using your OCR API, then process them through the existing assessment algorithms.

## Files Created/Modified

### 1. Configuration (`settings_local.py`)
- Added `OCR_API_SETTINGS` configuration section
- Configure your actual API URL, key, and parameters

### 2. OCR Utilities (`student/ocr_utils.py`)
- `OCRProcessor` class handles API communication
- Validates images, converts to base64, calls your OCR API
- Handles errors and returns structured responses

### 3. Forms (`student/forms.py`)
- `OCRAnswerSheetForm` for uploading answer sheets
- File validation, student/question selection
- Manual text override option

### 4. Views (`student/views.py`)
- `ocr_upload_answer_sheet()` - Main upload and processing view
- `ocr_processing_status()` - View recent OCR processed answers
- Integrates with existing `StudentAnswer` model

### 5. Templates
- `student/templates/student/ocr_upload.html` - Upload interface
- `student/templates/student/ocr_status.html` - Status dashboard

### 6. URLs (`student/urls.py`)
- `/student/ocr/upload/` - Upload answer sheets
- `/student/ocr/status/` - View processing status

### 7. Configuration Script (`configure_ocr.py`)
- Helper script to set up your OCR API details

## How to Use

### Step 1: Configure Your OCR API
```bash
cd /Applications/intemass-live_master
python3 configure_ocr.py
```

Enter your actual OCR API details:
- API URL: `https://your-actual-ocr-api.com/extract-text`
- API Key: Your authentication key (if required)
- Timeout and file size limits

### Step 2: Install Dependencies
```bash
pip3 install requests Pillow
```

### Step 3: Run the Django Server
```bash
python3 manage.py runserver
```

### Step 4: Access OCR Upload
Navigate to: `http://localhost:8000/student/ocr/upload/`

## Workflow

1. **Upload**: Teacher uploads handwritten answer sheet image
2. **API Call**: System calls your OCR API with the image
3. **Text Extraction**: OCR API returns digitized text
4. **Database Storage**: Text stored in `StudentAnswer` model
5. **Assessment**: Existing algorithms process the text
6. **Scoring**: Automatic scoring and feedback generation

## Integration Points

### Your OCR API Format Expected:
```json
POST https://your-ocr-api.com/extract-text
Headers: {
  "Content-Type": "application/json",
  "Authorization": "Bearer YOUR_API_KEY"
}
Body: {
  "image": "base64_encoded_image_data",
  "format": "jpg"
}

Response: {
  "extracted_text": "The handwritten text content...",
  "confidence": 0.95
}
```

### Database Integration:
The extracted text populates these `StudentAnswer` fields:
- `txt_answer`: Raw OCR text
- `student`: Selected student profile
- `question`: Selected question
- `timestamp`: Processing time
- `feedback`: Processing method info
- `feedback_code`: OCR confidence score

## Features

✅ **File Upload Validation**: Size and format checking
✅ **Multiple Formats**: JPG, PNG, PDF, TIFF support  
✅ **Manual Override**: Fallback for OCR failures
✅ **Student/Question Mapping**: Proper data association
✅ **Error Handling**: Graceful API failure handling
✅ **Processing Status**: Dashboard to monitor results
✅ **Assessment Integration**: Automatic scoring via existing algorithms

## Next Steps

1. **Configure your actual OCR API details**
2. **Test with sample answer sheets**
3. **Review and adjust scoring algorithms if needed**
4. **Train teachers on the upload process**
5. **Monitor OCR accuracy and adjust thresholds**

## Customization Options

- Adjust file size limits in `OCR_API_SETTINGS`
- Modify supported image formats
- Customize assessment scoring weights
- Add additional validation rules
- Implement batch processing for multiple sheets

The integration is ready to use with your OCR API! Just configure the API details and start processing handwritten answer sheets.
