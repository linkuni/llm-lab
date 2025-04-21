import json
from app.extensions import get_nlp, get_bedrock_client
from app.services.summarization_service import format_llama3_prompt, smart_chunk_text

def generate_questions_chunk(text, context=None, max_questions=5):
    """
    Generate exam questions for a chunk of text
    
    Args:
        text (str): Text chunk to generate questions from
        context (str, optional): Document context for improved question generation
        max_questions (int): Maximum number of questions to generate
        
    Returns:
        list: List of question objects with question, answer, key_points, and tips
    """
    bedrock_runtime = get_bedrock_client()
    
    user_prompt = (
        "You are an expert exam question generator for academic documents. Based on the following content, generate a diverse list of possible exam questions. For each question, provide:\n"
        "- The question (clear and concise)\n"
        "- The ideal answer (as expected by an examiner)\n"
        "- Key points required for full marks (as a list)\n"
        "- Tips to maximize marks (as a list)\n\n"
        f"Generate up to {max_questions} questions. Respond as a JSON array of objects, each with the keys: \"question\", \"answer\", \"key_points\", \"tips\".\n"
        "Only include questions that are relevant and significant to the document content. Do not include empty or placeholder values. Respond with only the JSON array and no other text.\n"
        + (f"Document context: {context}\n" if context else "") +
        "Here is the document:\n"
        "```\n"
        f"{text}\n"
        "```"
    )
    
    prompt = format_llama3_prompt(user_prompt)
    
    try:
        request_body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 2048,
            "temperature": 0.4,
            "top_p": 0.9
        })
        
        for _ in range(3):  # Retry up to 3 times
            response = bedrock_runtime.invoke_model(
                modelId="meta.llama3-70b-instruct-v1:0",
                contentType="application/json",
                accept="application/json",
                body=request_body
            )
            
            response_body = json.loads(response['body'].read().decode('utf-8'))
            questions = response_body.get('generation', '').strip()
            
            if questions:
                try:
                    parsed = json.loads(questions)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    continue
                    
        return []
    except Exception as e:
        print(f"Error in question generation: {str(e)}")
        return []

def recursive_generate_questions(text, max_words=400, max_questions=5):
    """
    Recursively generate questions from a document by chunking and processing
    
    Args:
        text (str): Full document text
        max_words (int): Maximum words per chunk
        max_questions (int): Maximum questions per chunk
        
    Returns:
        list: List of unique questions with answers, key points, and tips
    """
    # 1. Chunk the document at semantic boundaries
    chunks = smart_chunk_text(text, max_words=max_words)
    
    # 2. Generate a short global context for coherence
    global_context = ""
    if len(text.split()) > max_words:
        # Use first chunk as context if document is long
        global_context = " ".join(chunks[:2])
    
    # 3. Generate questions for each chunk
    all_questions = []
    for chunk in chunks:
        questions = generate_questions_chunk(chunk, context=global_context, max_questions=max_questions)
        all_questions.extend(questions)
    
    # 4. Deduplicate by question text
    seen = set()
    unique_questions = []
    for q in all_questions:
        q_text = q.get("question", "").strip().lower()
        if q_text and q_text not in seen:
            seen.add(q_text)
            unique_questions.append(q)
            
    return unique_questions 