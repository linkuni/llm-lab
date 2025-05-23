from flask import Blueprint, request, jsonify
import os
from app.services.pdf_service import extract_text_from_pdf, save_temp_file, remove_temp_file
from app.services.summarization_service import recursive_summarize
from app.services.question_service import recursive_generate_questions
from app.services.image_to_text_service import extract_text_from_file
from app.services.academic_assistant_service import generate_answers_for_all_questions
from app.services.preprocess import preprocess_question_paper

# Create blueprint for API v1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1.route('/summarize', methods=['POST'])
def summarize():
    """Endpoint to extract text from PDF and generate a summary"""
    print("summarize called")
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    temp_path = "temp.pdf"
    
    try:
        # Save uploaded file to temporary location
        save_temp_file(file, temp_path)
        
        # Extract text from PDF
        text_dict, all_text = extract_text_from_pdf(temp_path)
        
        # Generate summary
        summary = recursive_summarize(all_text, max_words=400)
        
        # Clean up temporary file
        remove_temp_file(temp_path)
        
        # Ensure summary is a proper JSON object, not a string
        if isinstance(summary, str):
            from app.services.summarization_service import extract_json_from_text
            summary = extract_json_from_text(summary)
        
        return jsonify({
            "text": text_dict,
            "summary": summary
        })

    except Exception as e:
        # Ensure temporary file is removed in case of error
        remove_temp_file(temp_path)
        return jsonify({"error": str(e)}), 500

@api_v1.route('/generate-questions', methods=['POST'])
def generate_questions():
    """Endpoint to extract text from PDF and generate exam questions"""
    print("generate_questions called")
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    # Get optional parameters with defaults
    max_questions = request.args.get('max_questions', default=5, type=int)
    max_words = request.args.get('max_words', default=400, type=int)

    temp_path = "temp.pdf"
    
    try:
        # Save uploaded file to temporary location
        save_temp_file(file, temp_path)
        
        # Extract text from PDF
        _, all_text = extract_text_from_pdf(temp_path)
        
        # Generate questions
        questions = recursive_generate_questions(all_text, max_words=max_words, max_questions=max_questions)
        
        # Clean up temporary file
        remove_temp_file(temp_path)
        
        return jsonify({
            "questions": questions
        })

    except Exception as e:
        # Ensure temporary file is removed in case of error
        remove_temp_file(temp_path)
        return jsonify({"error": str(e)}), 500

@api_v1.route('/academic-assistant', methods=['POST'])
def academic_assistant():
    """Endpoint to extract text from an image or PDF and generate academic answers"""
    print("academic_assistant called")
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        # Extract text from the uploaded file (image or PDF)
        extracted_text = extract_text_from_file(file)

        # Preprocess the extracted text
        preprocessed_text = preprocess_question_paper(extracted_text)
        
        # Generate academic answer using Llama
        model_response = generate_answers_for_all_questions(preprocessed_text)
        
        # Ensure model_response is a dictionary
        if not isinstance(model_response, dict):
            model_response = {"error": "Failed to generate a structured response", "raw_response": str(model_response)}
        
        return jsonify({
            "extracted_text": extracted_text,
            "preprocessed_text": preprocessed_text,
            "answer": model_response
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_v1.route('/test', methods=['GET'])
def test():
    """Simple test endpoint to verify API is functioning"""
    return jsonify({"message": "Hello, World!"}) 