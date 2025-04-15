import os
import json
from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from flask_cors import CORS
import boto3
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

# Set up AWS Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION'),  # Change to your AWS region
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def summarize_text(text):
    try:
        prompt = (
            "You are an expert summarization assistant with strong markdown formatting skills. "
            "Your task is to produce a comprehensive and complete summary of the provided document. "
            "The output should capture all the major themes, insights, and arguments present in the text, "
            "presented in a clear, coherent narrative. Start with an **Overview** section that outlines the overall message of the document, "
            "followed by detailed explanations that connect all important points together. "
            "Focus on being thorough and ensuring that nothing important is omitted. "
            "Keep the entire summary within a maximum of 1024 tokens. "
            "Here is the extracted text from the document:\n\n" + text
        )
        
        # Request body as a JSON string for Bedrock API call.
        request_body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 1024, 
            "temperature": 0.5,
            "top_p": 0.9
        })
        
        # Call Bedrock API with the specified format.
        response = bedrock_runtime.invoke_model(
            modelId="meta.llama3-70b-instruct-v1:0",
            contentType="application/json",
            accept="application/json",
            body=request_body
        )
        
        # Parse the API response.
        response_body = json.loads(response['body'].read().decode('utf-8'))
        summary = response_body.get('generation', '')
        
        return summary
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return "Failed to generate summary."

@app.route('/api/v1/extract-text', methods=['POST'])
def extract_text():
    print("extract_text called")
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Save the uploaded file temporarily
    temp_path = "temp.pdf"
    file.save(temp_path)
    
    try:
        # Extract text from PDF
        doc = fitz.open(temp_path)
        result = {}
        all_text = ""
        
        for i, page in enumerate(doc):
            text = page.get_text()
            result[i+1] = text
            all_text += text + "\n"
        
        # Close and remove temp file
        doc.close()
        os.remove(temp_path)
        
        # Generate a summary of the entire document
        summary = summarize_text(all_text[:10000])  # Limit text size to avoid token limits
        
        return jsonify({
            "text": result,
            "summary": summary
        })
    
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/v1/test', methods=['GET'])
def test():
    return jsonify({"message": "Hello, World!"})

if __name__ == "__main__":
    app.run(debug=True)