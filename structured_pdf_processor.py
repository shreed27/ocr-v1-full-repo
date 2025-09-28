#!/usr/bin/env python3
"""
Structured PDF OCR Processor
Processes PDFs and generates well-formatted, structured output for student answer sheets
"""

import requests
import json
import sys
import os
from datetime import datetime
import argparse

class StructuredPDFProcessor:
    def __init__(self, ocr_api_url="http://localhost:8080/api/process"):
        self.ocr_api_url = ocr_api_url
        self.results = {}
    
    def process_pdf(self, pdf_path):
        """Process a PDF and return structured results"""
        print(f"🔍 Processing PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            return {"error": f"PDF file not found: {pdf_path}"}
        
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(self.ocr_api_url, files=files, timeout=300)  # 5 minutes timeout
            
            print(f"📡 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ OCR Processing successful: {len(result.get('pages', []))} pages processed")
                return result
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def format_structured_output(self, ocr_results, pdf_filename):
        """Format OCR results into a well-structured output"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        student_name = pdf_filename.replace('.pdf', '').replace('_', ' ').title()
        
        structured_output = {
            "document_info": {
                "student_name": student_name,
                "filename": pdf_filename,
                "processed_at": timestamp,
                "total_pages": ocr_results.get("total_pages", 0),
                "processing_status": "completed" if "pages" in ocr_results else "failed"
            },
            "extraction_summary": {
                "pages_processed": 0,
                "total_characters": 0,
                "pages_with_content": 0,
                "average_chars_per_page": 0
            },
            "page_content": [],
            "full_document_text": "",
            "answers_by_question": {}
        }
        
        if "error" in ocr_results:
            structured_output["document_info"]["processing_status"] = "error"
            structured_output["error"] = ocr_results["error"]
            return structured_output
        
        full_text = []
        total_chars = 0
        pages_with_content = 0
        
        for page in ocr_results.get("pages", []):
            page_num = page.get("page", 0)
            extracted_text = page.get("extracted_text", "").strip()
            
            if extracted_text:
                pages_with_content += 1
                total_chars += len(extracted_text)
                full_text.append(f"[Page {page_num}] {extracted_text}")
            
            page_info = {
                "page_number": page_num,
                "character_count": len(extracted_text),
                "has_content": bool(extracted_text),
                "extracted_text": extracted_text,
                "text_preview": extracted_text[:100] + "..." if len(extracted_text) > 100 else extracted_text
            }
            
            structured_output["page_content"].append(page_info)
        
        # Update summary
        structured_output["extraction_summary"]["pages_processed"] = len(ocr_results.get("pages", []))
        structured_output["extraction_summary"]["total_characters"] = total_chars
        structured_output["extraction_summary"]["pages_with_content"] = pages_with_content
        structured_output["extraction_summary"]["average_chars_per_page"] = total_chars / max(pages_with_content, 1)
        
        structured_output["full_document_text"] = " ".join(full_text)
        
        # Try to identify answers by common patterns
        structured_output["answers_by_question"] = self.extract_answers_by_questions(structured_output["page_content"])
        
        return structured_output
    
    def extract_answers_by_questions(self, page_content):
        """Attempt to identify individual question answers"""
        answers = {}
        question_patterns = [
            "Q1", "Q2", "Q3", "Q4", "Q5",
            "Question 1", "Question 2", "Question 3", "Question 4", "Question 5",
            "1.", "2.", "3.", "4.", "5.",
            "a)", "b)", "c)", "d)", "e)"
        ]
        
        current_question = None
        current_answer = []
        
        for page in page_content:
            text = page.get("extracted_text", "")
            lines = text.split('.')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this line starts a new question
                question_found = False
                for pattern in question_patterns:
                    if line.upper().startswith(pattern.upper()):
                        # Save previous answer if exists
                        if current_question and current_answer:
                            answers[current_question] = " ".join(current_answer).strip()
                        
                        current_question = pattern
                        current_answer = [line.replace(pattern, "").strip()]
                        question_found = True
                        break
                
                if not question_found and current_question:
                    current_answer.append(line)
        
        # Save the last answer
        if current_question and current_answer:
            answers[current_question] = " ".join(current_answer).strip()
        
        return answers
    
    def save_results(self, structured_output, output_file):
        """Save structured results to a JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(structured_output, f, indent=2, ensure_ascii=False)
            print(f"✅ Results saved to: {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")
            return False
    
    def generate_report(self, structured_output):
        """Generate a human-readable report"""
        doc_info = structured_output["document_info"]
        summary = structured_output["extraction_summary"]
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                        STUDENT ANSWER SHEET ANALYSIS                     ║
╚══════════════════════════════════════════════════════════════════════════╝

📋 DOCUMENT INFORMATION:
   Student Name: {doc_info['student_name']}
   File Name: {doc_info['filename']}
   Processed: {doc_info['processed_at']}
   Status: {doc_info['processing_status'].upper()}

📊 EXTRACTION SUMMARY:
   Total Pages: {summary['pages_processed']}
   Pages with Content: {summary['pages_with_content']}
   Total Characters: {summary['total_characters']:,}
   Average Chars/Page: {summary['average_chars_per_page']:.1f}

📄 PAGE-BY-PAGE CONTENT:
"""
        
        for page in structured_output["page_content"]:
            status_icon = "✅" if page["has_content"] else "❌"
            report += f"   {status_icon} Page {page['page_number']}: {page['character_count']} characters\n"
            if page["has_content"]:
                report += f"      Preview: {page['text_preview']}\n\n"
        
        if structured_output["answers_by_question"]:
            report += "\n🎯 IDENTIFIED QUESTIONS & ANSWERS:\n"
            for q, answer in structured_output["answers_by_question"].items():
                report += f"   {q}: {answer[:150]}{'...' if len(answer) > 150 else ''}\n\n"
        
        report += f"\n📝 FULL EXTRACTED TEXT:\n{structured_output['full_document_text']}\n"
        
        report += "\n" + "="*80 + "\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Process PDF with structured OCR output")
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    parser.add_argument("--output", "-o", help="Output file path (optional)")
    parser.add_argument("--api-url", help="OCR API URL", default="http://localhost:8080/api/process")
    
    args = parser.parse_args()
    
    processor = StructuredPDFProcessor(args.api_url)
    
    # Process PDF
    print("🚀 Starting structured PDF processing...")
    ocr_results = processor.process_pdf(args.pdf_path)
    
    # Generate structured output
    pdf_filename = os.path.basename(args.pdf_path)
    structured_output = processor.format_structured_output(ocr_results, pdf_filename)
    
    # Generate report
    report = processor.generate_report(structured_output)
    print(report)
    
    # Save results if output file specified
    if args.output:
        processor.save_results(structured_output, args.output)
    else:
        # Save to default location
        base_name = pdf_filename.replace('.pdf', '')
        json_output = f"{base_name}_structured_ocr_results.json"
        processor.save_results(structured_output, json_output)
        
        # Also save the report
        report_output = f"{base_name}_ocr_report.txt"
        with open(report_output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_output}")

if __name__ == "__main__":
    main()
