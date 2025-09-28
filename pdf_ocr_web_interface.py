#!/usr/bin/env python3
"""
Simple Web Interface for PDF OCR Processing
Upload PDFs and get structured OCR results
"""

from flask import Flask, request, jsonify, render_template_string, send_file
import os
import tempfile
import json
from structured_pdf_processor import StructuredPDFProcessor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF OCR Processor</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container { 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #2c3e50; 
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-section {
            border: 2px dashed #3498db;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            margin-bottom: 20px;
            background-color: #ecf0f1;
        }
        .file-input {
            margin: 10px 0;
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #2980b9; }
        #results {
            margin-top: 20px;
            padding: 20px;
            border-radius: 5px;
            background-color: #2c3e50;
            color: #ecf0f1;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            display: none;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #3498db;
        }
        .success { background-color: #27ae60; }
        .error { background-color: #e74c3c; }
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            text-align: center;
        }
        .stat-box {
            background: #34495e;
            color: white;
            padding: 15px;
            border-radius: 5px;
            flex: 1;
            margin: 0 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 Student Answer Sheet OCR Processor</h1>
        
        <div class="upload-section">
            <h3>📤 Upload PDF Answer Sheet</h3>
            <p>Upload a student answer sheet PDF to extract handwritten text</p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="file-input">
                    <input type="file" id="pdfFile" name="pdf" accept=".pdf" required>
                </div>
                <button type="submit">🔍 Process PDF</button>
            </form>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            <p>🔄 Processing PDF... This may take a few moments.</p>
        </div>
        
        <div id="stats" style="display: none;">
            <div class="stats">
                <div class="stat-box">
                    <strong>📋 Student</strong><br>
                    <span id="studentName">-</span>
                </div>
                <div class="stat-box">
                    <strong>📄 Pages</strong><br>
                    <span id="totalPages">-</span>
                </div>
                <div class="stat-box">
                    <strong>📝 Characters</strong><br>
                    <span id="totalChars">-</span>
                </div>
                <div class="stat-box">
                    <strong>⭐ Status</strong><br>
                    <span id="status">-</span>
                </div>
            </div>
        </div>
        
        <div id="results"></div>
        
        <div id="download" style="display: none; text-align: center; margin-top: 20px;">
            <button onclick="downloadResults()">💾 Download Results</button>
            <button onclick="downloadReport()">📄 Download Report</button>
        </div>
    </div>

    <script>
        let currentResults = null;
        
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('pdfFile');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a PDF file');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('stats').style.display = 'none';
            document.getElementById('download').style.display = 'none';
            
            const formData = new FormData();
            formData.append('pdf', file);
            
            try {
                const response = await fetch('/process_pdf', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                currentResults = result;
                
                // Hide loading
                document.getElementById('loading').style.display = 'none';
                
                if (result.error) {
                    showResults(result.error, 'error');
                } else {
                    showStructuredResults(result);
                }
                
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                showResults('Error: ' + error.message, 'error');
            }
        });
        
        function showStructuredResults(result) {
            const docInfo = result.document_info;
            const summary = result.extraction_summary;
            
            // Update stats
            document.getElementById('studentName').textContent = docInfo.student_name;
            document.getElementById('totalPages').textContent = summary.pages_processed;
            document.getElementById('totalChars').textContent = summary.total_characters;
            document.getElementById('status').textContent = docInfo.processing_status.toUpperCase();
            
            document.getElementById('stats').style.display = 'block';
            
            // Show detailed results
            let output = `╔══════════════════════════════════════════════════════════════════════════╗\\n`;
            output += `║                        STUDENT ANSWER SHEET ANALYSIS                     ║\\n`;
            output += `╚══════════════════════════════════════════════════════════════════════════╝\\n\\n`;
            
            output += `📋 DOCUMENT INFORMATION:\\n`;
            output += `   Student Name: ${docInfo.student_name}\\n`;
            output += `   File Name: ${docInfo.filename}\\n`;
            output += `   Processed: ${docInfo.processed_at}\\n`;
            output += `   Status: ${docInfo.processing_status.toUpperCase()}\\n\\n`;
            
            output += `📊 EXTRACTION SUMMARY:\\n`;
            output += `   Total Pages: ${summary.pages_processed}\\n`;
            output += `   Pages with Content: ${summary.pages_with_content}\\n`;
            output += `   Total Characters: ${summary.total_characters.toLocaleString()}\\n`;
            output += `   Average Chars/Page: ${summary.average_chars_per_page.toFixed(1)}\\n\\n`;
            
            output += `📄 PAGE-BY-PAGE CONTENT:\\n`;
            result.page_content.forEach(page => {
                const icon = page.has_content ? '✅' : '❌';
                output += `   ${icon} Page ${page.page_number}: ${page.character_count} characters\\n`;
                if (page.has_content) {
                    output += `      Preview: ${page.text_preview}\\n\\n`;
                }
            });
            
            output += `\\n📝 FULL EXTRACTED TEXT:\\n`;
            output += result.full_document_text;
            
            showResults(output, 'success');
            document.getElementById('download').style.display = 'block';
        }
        
        function showResults(text, type = 'success') {
            const resultsDiv = document.getElementById('results');
            resultsDiv.textContent = text;
            resultsDiv.className = type;
            resultsDiv.style.display = 'block';
        }
        
        async function downloadResults() {
            if (!currentResults) return;
            
            const blob = new Blob([JSON.stringify(currentResults, null, 2)], {
                type: 'application/json'
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentResults.document_info.filename.replace('.pdf', '_ocr_results.json');
            a.click();
        }
        
        async function downloadReport() {
            if (!currentResults) return;
            
            const response = await fetch('/generate_report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentResults)
            });
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentResults.document_info.filename.replace('.pdf', '_ocr_report.txt');
            a.click();
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file uploaded'}), 400
        
        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not pdf_file.filename or not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Process the PDF
            processor = StructuredPDFProcessor()
            ocr_results = processor.process_pdf(tmp_path)
            
            # Generate structured output
            structured_output = processor.format_structured_output(
                ocr_results, 
                pdf_file.filename
            )
            
            return jsonify(structured_output)
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        structured_data = request.json
        processor = StructuredPDFProcessor()
        report = processor.generate_report(structured_data)
        
        # Create temporary file for report
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
            tmp_file.write(report)
            tmp_path = tmp_file.name
        
        return send_file(tmp_path, as_attachment=True, download_name='ocr_report.txt', mimetype='text/plain')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Starting PDF OCR Web Interface...")
    print("📍 Access at: http://localhost:5000")
    print("📄 Upload PDFs and get structured OCR results")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
