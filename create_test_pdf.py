#!/usr/bin/env python3
"""
Create a simple test PDF for testing the OCR API
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

def create_test_pdf(filename="test_document.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Page 1
    story.append(Paragraph("Test Document - Page 1", styles['h1']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("This is the first page of our test document.", styles['Normal']))
    story.append(Paragraph("It contains some sample text for OCR testing.", styles['Normal']))
    story.append(Paragraph("The text should be extracted accurately.", styles['Normal']))
    story.append(PageBreak())

    # Page 2
    story.append(Paragraph("Test Document - Page 2", styles['h1']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("This is the second page of our test document.", styles['Normal']))
    story.append(Paragraph("More sample text for testing purposes.", styles['Normal']))
    story.append(Paragraph("OCR should work well with this content.", styles['Normal']))
    story.append(PageBreak())

    # Page 3
    story.append(Paragraph("Test Document - Page 3", styles['h1']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("This is the third page of our test document.", styles['Normal']))
    story.append(Paragraph("Final page with test content.", styles['Normal']))
    story.append(Paragraph("All pages should be processed correctly.", styles['Normal']))

    try:
        doc.build(story)
        print(f"✅ Test PDF created: {filename}")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")

if __name__ == "__main__":
    create_test_pdf()
