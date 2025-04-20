import os
import json
from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from flask_cors import CORS
import boto3
from dotenv import load_dotenv
import spacy

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://api.linkuni.in"}})

nlp = spacy.load("en_core_web_sm")

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

SUMMARY_KEYS = [
    "title",
    "overview",
    "main_points",
    "important_terms",
    "benefits",
    "risks_or_limitations",
    "recommendations",
    "conclusion"
]

def format_llama3_prompt(user_prompt):
    # Required format for Llama 3 on AWS Bedrock
    return (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        + user_prompt +
        "\n<|start_header_id|>assistant<|end_header_id|>\n\n"
    )

def smart_chunk_text(text, max_words=400):
    doc = nlp(text)
    chunks = []
    current_chunk = []
    current_len = 0
    for sent in doc.sents:
        sent_words = len(sent.text.split())
        if current_len + sent_words > max_words and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0
        current_chunk.append(sent.text)
        current_len += sent_words
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def summarize_text(text, context=None, is_final=False):
    if is_final:
        user_prompt = (
            "You are an expert academic summarization assistant. Summarize the following document as a JSON object with the following keys if relevant: "
            "title, overview, main_points, important_terms, benefits, risks_or_limitations, recommendations, conclusion. "
            "Only include keys that are relevant and present in the document. "
            "main_points and important_terms should be lists; others should be strings. "
            "Do not include empty or placeholder values. Respond with a valid JSON object and no other text.\n\n"
            "Here are the chunk summaries:\n"
            "```"
            f"{text}\n"
            "```"
        )
    else:
        user_prompt = (
            "You are an expert academic summarization assistant. The following text is a section of a larger document. "
            + (f"Document context: {context}\n" if context else "")
            + "Summarize the key points from this section that relate to the following aspects: title, overview, main_points, important_terms, benefits, risks_or_limitations, recommendations, conclusion. "
            "Only include keys that are relevant and present in the section. "
            "main_points and important_terms should be lists; others should be strings. "
            "Do not include empty or placeholder values. Respond with a valid JSON object and no other text.\n"
            "Here is the section:\n"
            "```"
            f"{text}\n"
            "```"
        )
    prompt = format_llama3_prompt(user_prompt)
    try:
        request_body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 1024,
            "temperature": 0.3,
            "top_p": 0.9
        })
        for _ in range(3):  # Retry up to 3 times if summary is empty
            response = bedrock_runtime.invoke_model(
                modelId="meta.llama3-70b-instruct-v1:0",
                contentType="application/json",
                accept="application/json",
                body=request_body
            )
            response_body = json.loads(response['body'].read().decode('utf-8'))
            summary = response_body.get('generation', '')
            summary = summary.strip()
            if summary:
                try:
                    # Try to parse JSON output for safety
                    return json.loads(summary)
                except Exception:
                    return summary
        return {"error": "Failed to generate summary (empty response)."}
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return {"error": "Failed to generate summary."}

def recursive_summarize(text, max_words=400):
    chunks = smart_chunk_text(text, max_words=max_words)
    global_context = summarize_text(text[:min(len(text), 4000)], is_final=False)
    chunk_summaries = []
    for chunk in chunks:
        summary = summarize_text(chunk, context=global_context)
        chunk_summaries.append(json.dumps(summary))
    combined_summary = "\n\n".join(chunk_summaries)
    if len(combined_summary.split()) > max_words * 2:
        return recursive_summarize(combined_summary, max_words=max_words)
    final_summary = summarize_text(combined_summary, is_final=True)
    return final_summary

@app.route('/api/v1/extract-text', methods=['POST'])
def extract_text():
    print("extract_text called")
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    temp_path = "temp.pdf"
    file.save(temp_path)

    try:
        doc = fitz.open(temp_path)
        result = {}
        all_text = ""
        for i, page in enumerate(doc):
            text = page.get_text()
            result[i+1] = text
            all_text += text + "\n"
        doc.close()
        os.remove(temp_path)

        summary = recursive_summarize(all_text, max_words=400)

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
    app.run(debug=True, host='0.0.0.0', port=5678)
