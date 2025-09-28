# OCR Gemini - Simple OCR API

A clean and simple OCR API built with FastAPI and TrOCR (Microsoft's Transformer-based OCR model). This project provides a straightforward way to extract text from PDF documents with clean JSON output.

## Features

### 🚀 **Simple & Clean**
- **TrOCR Integration**: Uses Microsoft's state-of-the-art TrOCR model
- **FastAPI Backend**: Modern, fast, and easy-to-use API
- **Clean JSON Output**: Simple, structured response format
- **PDF Processing**: Extract text from PDF documents page by page

### 📄 **Document Processing**
- **PDF Support**: Process PDF documents
- **Page-by-Page Extraction**: Get text from each page separately
- **GPU Acceleration**: CUDA support for faster processing
- **Clean Output**: Structured JSON with page numbers and extracted text

### 🔧 **API Features**
- **RESTful API**: Simple HTTP endpoints
- **CORS Support**: Cross-origin requests enabled
- **Health Check**: Built-in health monitoring
- **Error Handling**: Graceful error responses

## Installation

### Prerequisites
- Python 3.8+
- CUDA support (optional, for GPU acceleration)
- 4GB+ RAM recommended

### Quick Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd "OCR Gemini"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the API**
```bash
python ocr_api.py
```

The API will be available at `http://localhost:8000`

## Usage

### API Endpoints

The API provides simple and clean endpoints:

#### **Health Check**
```bash
curl "http://localhost:8000/health"
```

#### **Upload and Extract Text**
```bash
# Upload PDF and extract text
curl -X POST "http://localhost:8000/api/v1/ocr/upload" \
  -F "file=@document.pdf"
```

#### **API Documentation**
Visit `http://localhost:8000/docs` for interactive API documentation.

### Example Response

```json
{
  "success": true,
  "filename": "document.pdf",
  "total_pages": 3,
  "pages": [
    {
      "page": 1,
      "text": "This is the extracted text from page 1 of your document."
    },
    {
      "page": 2,
      "text": "This is the extracted text from page 2 of your document."
    },
    {
      "page": 3,
      "text": "This is the extracted text from page 3 of your document."
    }
  ]
}
```

## Project Structure

```
OCR Gemini/
├── ocr_api.py          # Main OCR API with TrOCR integration
├── simple_api.py       # Simple API without OCR processing
├── create_test_pdf.py  # Utility to create test PDFs
├── requirements.txt    # Python dependencies
├── test_document.pdf   # Sample test document
└── README.md          # This file
```

## Features

- **TrOCR Model**: Uses Microsoft's Transformer-based OCR
- **FastAPI**: Modern, fast web framework
- **PDF Processing**: Extract text from PDF documents
- **Clean JSON Output**: Simple, structured responses
- **GPU Support**: Optional CUDA acceleration

## Testing

### Test the API
```bash
# Start the API
python ocr_api.py

# Test health endpoint
curl "http://localhost:8000/health"

# Test OCR endpoint
curl -X POST "http://localhost:8000/api/v1/ocr/upload" \
  -F "file=@test_document.pdf"
```

### Create Test PDF
```bash
# Generate a test PDF
python create_test_pdf.py
```

## Troubleshooting

### Common Issues

1. **Model Loading Issues**
   - Ensure you have sufficient RAM (4GB+)
   - Check internet connection for model download
   - Clear cache if needed: `rm -rf ~/.cache/transformers`

2. **CUDA/GPU Issues**
   ```bash
   # Check CUDA installation
   nvidia-smi
   
   # Install CUDA-compatible PyTorch
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Memory Issues**
   - Close other applications
   - Use CPU-only mode if GPU memory is insufficient

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue on GitHub
- Check the API docs at `http://localhost:8000/docs`
