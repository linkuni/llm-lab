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

## Requirements

- Python 3.8+
- Flask
- flask_cors
- boto3
- python-dotenv
- PyMuPDF
- spaCy (`en_core_web_sm`)

