import os
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary with page numbers as keys and extracted text as values
        str: All text combined
    """
    try:
        doc = fitz.open(file_path)
        result = {}
        all_text = ""
        
        for i, page in enumerate(doc):
            text = page.get_text()
            result[i+1] = text
            all_text += text + "\n"
            
        doc.close()
        return result, all_text
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def save_temp_file(file_obj, temp_path="temp.pdf"):
    """
    Save uploaded file to a temporary location
    
    Args:
        file_obj: File object from request
        temp_path (str): Path where to save the temporary file
        
    Returns:
        str: Path to the saved temporary file
    """
    file_obj.save(temp_path)
    return temp_path

def remove_temp_file(temp_path):
    """
    Remove temporary file
    
    Args:
        temp_path (str): Path to the temporary file
    """
    if os.path.exists(temp_path):
        os.remove(temp_path) 