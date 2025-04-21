# Document Summarizer

A robust, production-ready Flask API for summarizing academic documents (notes, guides, short notes, papers, etc.) into structured JSON summaries using AWS Bedrock Llama 3.  
The service extracts text from PDFs, recursively chunks and summarizes content, and outputs key-value summaries optimized for frontend use—even for long documents that exceed LLM token limits.

---

## Features

- **Handles Any Academic Document:** Works for notes, guides, short notes, research papers, and more.
- **Structured JSON Output:** Summaries are returned as key-value pairs (e.g., `title`, `overview`, `main_points`, etc.) for easy frontend integration.
- **Token-Limit Resilient:** Uses recursive chunking and map-reduce summarization to handle documents of any length, overcoming LLM context window/token limitations.
- **Context-Aware Summarization:** Each chunk summary is enriched with global document context for coherence and completeness.
- **Bedrock Llama 3 Optimized:** Uses the required prompt formatting for reliable responses from AWS Bedrock Llama 3 models.
- **Automatic Retry:** Retries summarization if the model returns an empty response.
- **Modular Architecture:** Uses a standard Flask application structure with proper separation of concerns for easy extension and maintenance.
- **Question Generation:** Automatically generates exam-style questions with answers, key points, and tips for maximizing marks.

---

## How It Works

### 1. **Text Extraction**
- Extracts all text from each page of the uploaded PDF using PyMuPDF.

### 2. **Semantic Chunking**
- Splits extracted text into coherent chunks at sentence boundaries (using spaCy), ensuring each chunk fits within the model's token limits.

### 3. **Recursive Map-Reduce Summarization**
- **Map Step:** Each chunk is summarized independently, with global document context prepended.
- **Reduce Step:** Summaries are combined and recursively summarized until the result fits within the token limit, preserving key information.
- **Final Synthesis:** The last step synthesizes all chunk summaries into a single, logically structured JSON summary.

### 4. **Prompt Engineering & Token Optimization**
- Prompts are carefully designed for clarity, conciseness, and structure, and use the required AWS Bedrock Llama 3 format to avoid empty or malformed responses.
- Only relevant keys are included in the final summary, with lists for `main_points` and `important_terms`, and strings for others.

### 5. **Question Generation**
- **Chunking:** Document is split into semantically coherent chunks to maintain context.
- **Context-Awareness:** Questions are generated with awareness of the entire document's context.
- **Deduplication:** Similar questions are filtered out to ensure variety and relevance.
- **Comprehensive Answers:** Each question includes an ideal answer, key points for full marks, and tips for maximizing scores.

---

## API Usage

### **POST** `/api/v1/extract-text`

#### **Request**
- `file`: PDF file (multipart/form-data)

#### **Response**
```js
{
"text": {
"1": "Page 1 text ...",
"2": "Page 2 text ...",
...
},
"summary": {
"title": "Cloud Computing Basics",
"overview": "This document explains the fundamentals of cloud computing...",
"main_points": [
"Definition and types of cloud computing",
"Benefits and risks",
"Choosing a provider"
],
"important_terms": [
"Public Cloud",
"Private Cloud",
"SaaS",
"PaaS",
"IaaS"
],
"benefits": "Scalability, flexibility, cost-effectiveness, reliability.",
"risks_or_limitations": "Security risks, vendor lock-in, loss of control.",
"conclusion": "Evaluate your needs and provider options before adopting cloud solutions."
}
}
```
- Only relevant keys are included for each document.

### **POST** `/api/v1/generate-questions`

#### **Request**
- `file`: PDF file (multipart/form-data)
- `max_questions` (optional): Maximum number of questions per chunk (default: 5)
- `max_words` (optional): Maximum words per chunk (default: 400)

#### **Response**
```js
{
"questions": [
{
"question": "What are the key characteristics of cloud computing?",
"answer": "Cloud computing is characterized by on-demand self-service, broad network access, resource pooling, rapid elasticity, and measured service. These characteristics enable organizations to access computing resources without significant upfront investment while scaling as needed.",
"key_points": [
"On-demand self-service without human interaction",
"Broad network access from various devices",
"Resource pooling with multi-tenancy",
"Rapid elasticity and scalability",
"Measured service with pay-as-you-go model"
],
"tips": [
"Use specific examples for each characteristic",
"Explain the business impact of each feature",
"Compare with traditional computing models",
"Cite industry standards or NIST definitions"
]
},
// More questions...
]
}
```

---

## Methods Used to Enhance Summaries with Limited Tokens

### **Chunking**
- Text is split into semantic chunks (by sentences, not arbitrary length), so each chunk fits within the LLM's token window.

### **Recursive Summarization (Map-Reduce)**
- Each chunk is summarized individually (map step).
- Summaries are recursively merged and summarized again (reduce step) until the output is concise and within the token limit.

### **Contextual Summarization**
- Each chunk summary includes global document context, improving coherence and reducing information loss.

### **Prompt Engineering & Token Optimization**
- Prompts are structured for clarity, minimal redundancy, and required output format.
- Uses Bedrock Llama 3's required prompt tokens for reliable results.
- Only relevant keys are included in the output, optimizing token usage.

---

## Development

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your AWS credentials and other settings:
   ```
   AWS_REGION=your-region
   AWS_ACCESS_KEY_ID=your-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-key
   CORS_ORIGIN=your-frontend-origin
   ```
4. Run the application: `python run.py`

### Adding New Features
1. Create a new service module in `app/services/` for business logic
2. Implement new API endpoints in `app/api/v1/routes.py` or create a new version in `app/api/v2/`
3. Update the configuration in `app/config.py` if needed

---

## Requirements

- Python 3.8+
- Flask
- flask_cors
- boto3
- python-dotenv
- PyMuPDF
- spaCy (`en_core_web_sm`)

