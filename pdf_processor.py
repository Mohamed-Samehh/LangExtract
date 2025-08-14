import fitz  # PyMuPDF
from docx import Document
import io
from PIL import Image
import streamlit as st

class PDFProcessor:
    def __init__(self):
        """Initialize the PDF processor."""
        pass
    
    def extract_text_from_pdf(self, pdf_file):
        """
        Extract text from PDF file using PyMuPDF (fitz).
        PyMuPDF is excellent for Arabic text extraction.
        """
        try:
            # Read the uploaded file
            pdf_bytes = pdf_file.read()
            
            # Open the PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                # Extract text with proper handling of RTL languages
                page_text = page.get_text()
                text += page_text + "\n"
            
            doc.close()
            return text.strip()
            
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX file."""
        try:
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            st.error(f"Error extracting text from DOCX: {str(e)}")
            return None
    
    def extract_text_from_txt(self, txt_file):
        """Extract text from TXT file."""
        try:
            # Try UTF-8 first, then fallback to other encodings
            try:
                text = txt_file.read().decode('utf-8')
            except UnicodeDecodeError:
                txt_file.seek(0)  # Reset file pointer
                try:
                    text = txt_file.read().decode('utf-8-sig')  # UTF-8 with BOM
                except UnicodeDecodeError:
                    txt_file.seek(0)
                    text = txt_file.read().decode('windows-1256')  # Arabic Windows encoding
            
            return text.strip()
        except Exception as e:
            st.error(f"Error extracting text from TXT: {str(e)}")
            return None
    
    def process_uploaded_file(self, uploaded_file):
        """Process uploaded file and extract text based on file type."""
        if uploaded_file is None:
            return None
        
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(uploaded_file)
        elif file_extension == 'docx':
            return self.extract_text_from_docx(uploaded_file)
        elif file_extension == 'txt':
            return self.extract_text_from_txt(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return None