# Intemass Assessment Platform with OCR Integration

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-3.2+-green.svg)
![OCR](https://img.shields.io/badge/OCR-Integration-orange.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

## 🎯 Overview

**Intemass Assessment Platform** is a comprehensive educational assessment system with integrated **Handwritten Answer Sheet OCR** capabilities. The platform automatically digitizes handwritten student responses and feeds them into an intelligent assessment workflow for automatic grading and feedback generation.

## ✨ Key Features

### 🖼️ **OCR Integration**
- **Handwritten Text Recognition**: Automatically converts handwritten answer sheets to digital text
- **Multi-format Support**: JPG, PNG, PDF, TIFF image formats
- **Real-time Processing**: Fast OCR processing with confidence scoring
- **Section Detection**: Automatic identification of sections (Section-A, Section-B, etc.)
- **Question Mapping**: Intelligent parsing of questions and answers

### 📚 **Assessment Platform**
- **Automatic Grading**: AI-powered assessment algorithms
- **Multi-choice Questions (MCQ)**: Complete MCQ handling system
- **Student Management**: Comprehensive student and class management
- **Teacher Dashboard**: Intuitive interface for educators
- **Report Generation**: Detailed performance analytics
- **Paper Management**: Question paper creation and management

### 🔧 **Technical Features**
- **Django 3.2**: Modern web framework
- **SQLite/MySQL**: Flexible database support
- **RESTful APIs**: Clean API architecture
- **File Upload**: Secure file handling with validation
- **Error Handling**: Comprehensive error management
- **Scalable Architecture**: Production-ready design

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Django 3.2+
- OCR API service running on localhost:8080

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/intemass-ocr-platform.git
   cd intemass-ocr-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings**
   ```bash
   cp settings_local.py.example settings_local.py
   # Edit settings_local.py with your configuration
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the server**
   ```bash
   python manage.py runserver
   ```

6. **Access OCR Interface**
   - Navigate to: `http://localhost:8000/student/ocr/upload/`
   - Upload handwritten answer sheets
   - View automatic processing results

## 📖 OCR Workflow

### 1. **Image Upload**
Teachers upload handwritten answer sheets through the web interface.

### 2. **OCR Processing**
The system sends images to the OCR API and receives structured data:
```json
{
  "status": "success",
  "data": {
    "metadata": {
      "filename": "answer_sheet.jpg",
      "processing_time_seconds": 1.2,
      "total_lines_detected": 7,
      "average_confidence": 0.85
    },
    "questions": [
      {
        "question_text": "Ques. 1",
        "answer_text": "Student's handwritten answer...",
        "confidence": 0.87
      }
    ],
    "raw_extracted_lines": [...],
    "section": "Section-A"
  }
}
```

### 3. **Database Storage**
Extracted text is saved to the `StudentAnswer` model with metadata.

### 4. **Automatic Assessment**
Assessment algorithms process the digitized text and generate scores.

### 5. **Results Dashboard**
Teachers can review results, edit OCR output if needed, and provide feedback.

## 🗂️ Project Structure

```
intemass-live_master/
├── student/                 # Student management & OCR integration
│   ├── ocr_utils.py        # OCR processing logic
│   ├── forms.py            # OCR upload forms
│   ├── views.py            # OCR views and handlers
│   └── templates/          # OCR interface templates
├── teacher/                # Teacher dashboard and tools
├── question/               # Question and paper management
├── mcq/                    # Multiple choice questions
├── assignment/             # Assignment handling
├── report/                 # Analytics and reporting
├── algo/                   # Assessment algorithms
├── settings_local.py       # Local configuration
├── requirements.txt        # Python dependencies
└── manage.py              # Django management
```

## ⚙️ Configuration

### OCR API Settings
```python
OCR_API_SETTINGS = {
    'API_URL': 'http://localhost:8080/api/process',
    'API_KEY': '',
    'TIMEOUT': 30,
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_FORMATS': ['jpg', 'jpeg', 'png', 'pdf', 'tiff'],
}
```

### Database Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## 🧪 Testing

### Run OCR Integration Tests
```bash
# Test OCR API connection
python test_file_upload.py

# Test with real handwritten image
python test_real_handwriting.py

# Complete end-to-end test
python test_end_to_end.py

# Production readiness report
python production_status_report.py
```

### Expected Test Results
- ✅ OCR API communication
- ✅ File upload validation
- ✅ Text extraction accuracy
- ✅ Django model integration
- ✅ Assessment workflow

## 📊 Features in Detail

### **OCR Processing Engine**
- **Microsoft TrOCR Model**: Advanced handwriting recognition
- **Confidence Scoring**: Quality assessment for each extracted line
- **Multi-line Support**: Complete answer reconstruction
- **Section Recognition**: Automatic section identification
- **Question Parsing**: Intelligent question-answer mapping

### **Assessment Algorithms**
- **Keyword Matching**: Content-based scoring
- **Semantic Analysis**: Understanding-based evaluation
- **Grammar Checking**: Language quality assessment
- **Answer Completeness**: Response thoroughness evaluation

### **Teacher Tools**
- **OCR Review Interface**: Edit and verify extracted text
- **Batch Processing**: Handle multiple answer sheets
- **Performance Analytics**: Student progress tracking
- **Feedback Generation**: Automated response creation

## 🔐 Security Features

- **File Validation**: Strict file type and size checking
- **Input Sanitization**: XSS and injection prevention
- **Access Control**: Role-based permissions
- **Secure Upload**: Protected file handling
- **Error Logging**: Comprehensive audit trail

## 🌟 Production Ready

This system is **production-ready** and includes:

- ✅ **Comprehensive Error Handling**
- ✅ **Input Validation and Sanitization**
- ✅ **Scalable Database Design**
- ✅ **RESTful API Architecture**
- ✅ **Detailed Logging and Monitoring**
- ✅ **Performance Optimization**
- ✅ **Security Best Practices**

## 📈 Performance

- **OCR Processing**: ~1-2 seconds per image
- **File Upload**: Up to 10MB per file
- **Concurrent Users**: Optimized for classroom scale
- **Database**: Efficient indexing and queries
- **Caching**: Smart result caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See `/docs` folder for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **Discussion**: Use GitHub Discussions for questions

## 🙏 Acknowledgments

- **TrOCR Model**: Microsoft's Transformer-based OCR
- **Django Community**: Web framework excellence
- **Contributors**: All project contributors

---

## 🎯 Live Demo

**OCR Integration Status**: ✅ **PRODUCTION READY**

Your handwritten answer sheet OCR integration is ready for production use! The system will automatically digitize handwritten student responses and feed them into your existing assessment workflow. 🎓✨

**Ready for Company Deployment** 🚀
