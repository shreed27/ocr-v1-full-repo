#!/usr/bin/env python3
"""
Batch PDF OCR Processor
Process multiple PDFs and save all results to text files
"""

import os
import sys
from structured_pdf_processor import StructuredPDFProcessor
from datetime import datetime

def process_multiple_pdfs(pdf_directory, output_directory="ocr_batch_results"):
    """Process multiple PDFs and save results to text files"""
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in directory")
        return
    
    # Limit to 10 files as requested
    pdf_files = pdf_files[:10]
    
    print(f"🚀 Starting batch processing of {len(pdf_files)} PDFs...")
    print(f"📂 Output directory: {output_directory}")
    print("="*80)
    
    processor = StructuredPDFProcessor()
    results_summary = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(pdf_directory, pdf_file)
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file}")
        print("-" * 60)
        
        try:
            # Process PDF
            ocr_results = processor.process_pdf(pdf_path)
            
            # Generate structured output
            structured_output = processor.format_structured_output(ocr_results, pdf_file)
            
            # Generate report
            report = processor.generate_report(structured_output)
            
            # Save results
            base_name = pdf_file.replace('.pdf', '').replace(' ', '_')
            
            # Save detailed report as TXT
            report_file = os.path.join(output_directory, f"{base_name}_detailed_report.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # Save JSON results
            json_file = os.path.join(output_directory, f"{base_name}_structured_data.json")
            processor.save_results(structured_output, json_file)
            
            # Save extracted text only
            text_file = os.path.join(output_directory, f"{base_name}_extracted_text.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"STUDENT: {structured_output['document_info']['student_name']}\n")
                f.write(f"FILE: {pdf_file}\n")
                f.write(f"PROCESSED: {structured_output['document_info']['processed_at']}\n")
                f.write("="*60 + "\n\n")
                f.write("EXTRACTED TEXT:\n")
                f.write("-"*30 + "\n")
                f.write(structured_output['full_document_text'])
                f.write("\n\n" + "="*60 + "\n")
            
            # Add to summary
            doc_info = structured_output['document_info']
            summary = structured_output['extraction_summary']
            
            results_summary.append({
                'file': pdf_file,
                'student': doc_info['student_name'],
                'status': doc_info['processing_status'],
                'pages': summary['pages_processed'],
                'chars': summary['total_characters'],
                'avg_chars': round(summary['average_chars_per_page'], 1)
            })
            
            # Print brief status
            status_icon = "✅" if doc_info['processing_status'] == 'completed' else "❌"
            print(f"{status_icon} Status: {doc_info['processing_status'].upper()}")
            print(f"📄 Pages: {summary['pages_processed']} | Characters: {summary['total_characters']}")
            print(f"💾 Saved: {report_file}")
            print(f"💾 Saved: {text_file}")
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
            results_summary.append({
                'file': pdf_file,
                'student': 'Unknown',
                'status': 'error',
                'pages': 0,
                'chars': 0,
                'avg_chars': 0
            })
    
    # Generate batch summary report
    generate_batch_summary(results_summary, output_directory)
    
    print("\n" + "="*80)
    print("🎉 BATCH PROCESSING COMPLETE!")
    print(f"📂 All results saved in: {output_directory}")
    print("="*80)

def generate_batch_summary(results_summary, output_directory):
    """Generate a summary report for all processed PDFs"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary_content = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                          BATCH OCR PROCESSING SUMMARY                    ║
╚══════════════════════════════════════════════════════════════════════════╝

📅 Processed: {timestamp}
📊 Total Files: {len(results_summary)}

📋 PROCESSING RESULTS:
{'='*80}
"""
    
    total_chars = 0
    successful = 0
    
    for i, result in enumerate(results_summary, 1):
        status_icon = "✅" if result['status'] == 'completed' else "❌"
        summary_content += f"""
[{i:2d}] {status_icon} {result['file']}
     Student: {result['student']}
     Status: {result['status'].upper()}
     Pages: {result['pages']} | Characters: {result['chars']:,} | Avg: {result['avg_chars']}/page
"""
        if result['status'] == 'completed':
            successful += 1
            total_chars += result['chars']
    
    summary_content += f"""
{'='*80}
📊 BATCH STATISTICS:
   • Successful: {successful}/{len(results_summary)} files ({successful/len(results_summary)*100:.1f}%)
   • Total Characters Extracted: {total_chars:,}
   • Average Characters per File: {total_chars/max(successful, 1):.1f}

📁 OUTPUT FILES GENERATED:
   • Detailed Reports: *_detailed_report.txt
   • Structured Data: *_structured_data.json  
   • Extracted Text: *_extracted_text.txt
   • Batch Summary: batch_summary_report.txt

🎯 All files ready for assessment processing!
{'='*80}
"""
    
    # Save batch summary
    summary_file = os.path.join(output_directory, "batch_summary_report.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"📄 Batch summary saved: {summary_file}")
    
    # Also print to terminal
    print(summary_content)

def main():
    pdf_directory = "/Applications/intemass-live_master/downloaded_pdfs/"
    
    print("🔍 Batch PDF OCR Processing Starting...")
    print(f"📂 Source Directory: {pdf_directory}")
    
    if not os.path.exists(pdf_directory):
        print(f"❌ Directory not found: {pdf_directory}")
        return
    
    process_multiple_pdfs(pdf_directory)

if __name__ == "__main__":
    main()
