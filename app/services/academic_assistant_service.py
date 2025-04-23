import json
from app.extensions import get_bedrock_client

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

def extract_json_from_text(text):
    """
    Extract a JSON object from text that may contain markdown code blocks or other text
    
    Args:
        text (str): Text potentially containing JSON
        
    Returns:
        dict: Extracted JSON object or error
    """

    if "```" in text:

        parts = text.split("```")
        for i in range(1, len(parts), 2):
            try:
                content = parts[i].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
                return json.loads(content)
            except json.JSONDecodeError:
                continue
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except:
            pass
            
    return {"error": "Could not extract valid JSON from response"}

def generate_academic_answer(question, context):
    """
    Generate an academic answer for an exam question using Llama
    
    Args:
        extracted_text (str): The extracted text containing the question
        
    Returns:
        dict: The generated academic answer in structured JSON format
    """
    bedrock_runtime = get_bedrock_client()
    
    prompt_template = (
        "You are an expert academic assistant. Based on the following question and context, "
        "write a comprehensive, well-structured answer suitable for an exam. "
        "Respond with a JSON object having the following structure:\n\n"
        "solution: {\n"
        "  \"question\": \"The extracted question text\",\n"
        "  \"introduction\": \"A brief introduction to the topic\",\n"
        "  \"key_concepts\": [\"List of key concepts and terms with explanations\"],\n"
        "  \"main_content\": \"The comprehensive answer content with proper organization\",\n"
        "  \"examples\": [\"Relevant examples or analogies\"],\n"
        "  \"conclusion\": \"A concise conclusion or summary\",\n"
        "  \"tips_for_maximum_marks\": [\"Strategies to impress examiners\", \"Ways to avoid common mistakes\"]\n"
        "}\n\n"
        "Ensure your response is a valid JSON object that can be parsed directly. "
        "Don't include any markdown formatting, only provide the JSON object. "
        "Don't include explanations or any text outside the JSON structure.\n\n"
        f"Question: {question}"
        f"Context: {context}"
    )
    
    prompt = format_llama3_prompt(prompt_template)
    
    try:
        request_body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 2048,
            "temperature": 0.4,
            "top_p": 0.9
        })
        
        response = bedrock_runtime.invoke_model(
            modelId="meta.llama3-70b-instruct-v1:0",
            contentType="application/json",
            accept="application/json",
            body=request_body
        )
        
        response_body = json.loads(response['body'].read().decode('utf-8'))
        answer_text = response_body.get('generation', '').strip()
        
        try:
            answer_json = json.loads(answer_text)
            return answer_json
        except json.JSONDecodeError:
            return extract_json_from_text(answer_text)
        
    except Exception as e:
        print(f"Error generating academic answer: {str(e)}")
        return {
            "error": f"Error generating academic answer: {str(e)}",
            "question": question,
            "introduction": "",
            "key_concepts": [],
            "main_content": "",
            "examples": [],
            "conclusion": "",
            "tips_for_maximum_marks": []
        } 
    
def generate_answers_for_all_questions(preprocessed_text):
    context = preprocessed_text["context"]
    questions = preprocessed_text["questions"]
    all_solutions = []
    for q in questions:
        answer = generate_academic_answer(
            question=q["question_text"],
            context=context,
        )
        answer["question_number"] = q["question_number"]
        answer["marks"] = q["marks"]
        all_solutions.append(answer)
    return {"solutions": all_solutions}