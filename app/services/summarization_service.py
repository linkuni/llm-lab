import json
from app.extensions import get_nlp, get_bedrock_client

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
    """
    Format prompt for Llama 3 model on AWS Bedrock
    
    Args:
        user_prompt (str): The user prompt content
        
    Returns:
        str: Formatted prompt for Llama 3
    """
    return (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        + user_prompt +
        "\n<|start_header_id|>assistant<|end_header_id|>\n\n"
    )

def smart_chunk_text(text, max_words=400):
    """
    Split text into semantic chunks using spaCy
    
    Args:
        text (str): Text to be chunked
        max_words (int): Maximum words per chunk
        
    Returns:
        list: List of text chunks
    """
    nlp = get_nlp()
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

def extract_json_from_text(text):
    """
    Extract a JSON object from text that may contain markdown code blocks or other text
    
    Args:
        text (str): Text potentially containing JSON
        
    Returns:
        dict: Extracted JSON object or error
    """
    # Check if the text contains a code block with JSON
    if "```" in text:
        # Extract content between code blocks
        parts = text.split("```")
        for i in range(1, len(parts), 2):
            try:
                # Try to parse as JSON, removing language identifier if present
                content = parts[i].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
                return json.loads(content)
            except json.JSONDecodeError:
                continue
    
    # If no valid JSON in code blocks, try parsing the whole text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # As a last resort, try to find anything that looks like a JSON object
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except:
            pass
            
    return {"error": "Could not extract valid JSON from response"}

def summarize_text(text, context=None, is_final=False):
    """
    Generate summary using AWS Bedrock
    
    Args:
        text (str): Text to summarize
        context (dict, optional): Context for the summarization
        is_final (bool): Whether this is the final summary
        
    Returns:
        dict: Summary in JSON format
    """
    bedrock_runtime = get_bedrock_client()
    
    if is_final:
        user_prompt = (
            "You are an expert academic summarization assistant. Summarize the following document as a JSON object with the following keys if relevant: "
            "title, overview, main_points, important_terms, benefits, risks_or_limitations, recommendations, conclusion. "
            "Only include keys that are relevant and present in the document. "
            "main_points and important_terms should be lists; others should be strings. "
            "Do not include empty or placeholder values. Respond with a valid JSON object and no other text, no markdown formatting, no ```json tags.\n\n"
            "Here are the chunk summaries:\n"
            "```\n"
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
            "Do not include empty or placeholder values. Respond with a valid JSON object and no other text, no markdown formatting, no ```json tags.\n"
            "Here is the section:\n"
            "```\n"
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
            summary = response_body.get('generation', '').strip()
            
            if summary:
                try:
                    # First try to directly parse as JSON
                    return json.loads(summary)
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON from text
                    return extract_json_from_text(summary)
                    
        return {"error": "Failed to generate summary (empty response)."}
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return {"error": f"Failed to generate summary: {str(e)}"}

def recursive_summarize(text, max_words=400):
    """
    Recursively summarize text by chunking and then combining summaries
    
    Args:
        text (str): Text to summarize
        max_words (int): Maximum words per chunk
        
    Returns:
        dict: Final summary in JSON format
    """
    chunks = smart_chunk_text(text, max_words=max_words)
    global_context = summarize_text(text[:min(len(text), 4000)], is_final=False)
    chunk_summaries = []
    
    for chunk in chunks:
        summary = summarize_text(chunk, context=global_context)
        # Ensure we're dealing with string representation of JSON objects
        if isinstance(summary, dict):
            chunk_summaries.append(json.dumps(summary))
        else:
            chunk_summaries.append(str(summary))
        
    combined_summary = "\n\n".join(chunk_summaries)
    
    if len(combined_summary.split()) > max_words * 2:
        return recursive_summarize(combined_summary, max_words=max_words)
        
    final_summary = summarize_text(combined_summary, is_final=True)
    return final_summary 