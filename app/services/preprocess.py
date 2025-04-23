import re

def preprocess_question_paper(text):
    # 1. Extract context (everything before first question)
    question_start = re.search(r'Q\.?1', text)
    context = text[:question_start.start()] if question_start else ""
    questions_section = text[question_start.start():] if question_start else text

    # 2. Split into questions (Q.1, Q.2, etc.)
    question_blocks = re.split(r'(Q\.?\d+)', questions_section)
    # re.split keeps the delimiter, so we need to pair them
    questions = []
    for i in range(1, len(question_blocks), 2):
        q_num = question_blocks[i].strip()
        q_text_block = question_blocks[i+1]
        # Extract marks (e.g., [5 Marks])
        marks = None
        marks_match = re.search(r'\[(\d+)\s*Marks?\]', q_text_block)
        if marks_match:
            marks = int(marks_match.group(1))
            q_text = re.sub(r'\[\d+\s*Marks?\]', '', q_text_block).strip()
        else:
            q_text = q_text_block.strip()
        questions.append({
            "question_number": q_num,
            "question_text": q_text,
            "marks": marks
        })

    return {
        "context": context.strip(),
        "questions": questions
    }
