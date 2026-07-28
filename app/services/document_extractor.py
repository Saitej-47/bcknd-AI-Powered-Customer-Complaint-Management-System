"""
Document Extractor - Extract text from PDF, DOCX, TXT, EML files
backend/app/services/document_extractor.py
"""

import PyPDF2
from typing import Tuple
import io

def extract_text_from_pdf(file_content: bytes) -> Tuple[str, bool]:
    """
    Extract text from PDF file
    
    Args:
        file_content: PDF file bytes
    
    Returns:
        Tuple of (extracted_text, success)
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text.strip(), True
    except Exception as e:
        return f"PDF extraction error: {str(e)}", False

def extract_text_from_txt(file_content: bytes) -> Tuple[str, bool]:
    """Extract text from plain text file"""
    try:
        text = file_content.decode('utf-8').strip()
        return text, True
    except Exception as e:
        return f"TXT extraction error: {str(e)}", False

def extract_text_from_eml(file_content: bytes) -> Tuple[str, bool]:
    """
    Extract text from EML (email) file
    """
    try:
        import email
        msg = email.message_from_bytes(file_content)
        
        # Get email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Get subject
        subject = msg.get("Subject", "")
        
        # Combine
        text = f"Subject: {subject}\n\n{body}"
        return text.strip(), True
    except Exception as e:
        return f"EML extraction error: {str(e)}", False

def extract_text_from_document(file_content: bytes, filename: str) -> Tuple[str, bool]:
    """
    Main function - extract text based on file type
    
    Args:
        file_content: File bytes
        filename: Original filename
    
    Returns:
        Tuple of (extracted_text, success)
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    elif filename_lower.endswith('.txt'):
        return extract_text_from_txt(file_content)
    elif filename_lower.endswith('.eml'):
        return extract_text_from_eml(file_content)
    elif filename_lower.endswith('.docx'):
        return extract_text_from_docx(file_content)
    else:
        return "Unsupported file type. Supported: PDF, TXT, EML, DOCX", False

def extract_text_from_docx(file_content: bytes) -> Tuple[str, bool]:
    """
    Extract text from DOCX file
    """
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip(), True
    except ImportError:
        # python-docx not installed
        return "DOCX support requires python-docx library", False
    except Exception as e:
        return f"DOCX extraction error: {str(e)}", False