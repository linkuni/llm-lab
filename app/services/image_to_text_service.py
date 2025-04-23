import os
import boto3
from app.services.pdf_service import save_temp_file

def extract_text_from_image(image_path):
    """
    Extract text from an image file using AWS Textract
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text
    """
    # Create a Textract client
    textract = boto3.client('textract')
    
    # Read the image file as bytes
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    
    response = textract.detect_document_text(Document={'Bytes': image_bytes})
    
    lines = []
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            lines.append(item['Text'])
    
    extracted_text = '\n'.join(lines)
    return extracted_text

def determine_file_type(file_obj):
    """
    Determine the type of the uploaded file
    
    Args:
        file_obj: File object from the request
        
    Returns:
        str: File type ('pdf', 'image', or 'unknown')
    """
    filename = file_obj.filename.lower()
    
    if filename.endswith('.pdf'):
        return 'pdf'
    elif any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
        return 'image'
    else:
        return 'unknown'

def extract_text_from_file(file_obj):
    """
    Extract text from a file (PDF or image)
    
    Args:
        file_obj: File object from the request
        
    Returns:
        str: Extracted text
    """
    file_type = determine_file_type(file_obj)
    temp_path = f"temp{os.path.splitext(file_obj.filename)[1]}"
    
    try:
        # Save uploaded file to temporary location
        save_temp_file(file_obj, temp_path)
        
        if file_type == 'pdf' or file_type == 'image':
            return extract_text_from_image(temp_path)
        else:
            raise ValueError(f"Unsupported file type: {file_obj.filename}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path) 