import json

def build_quiz_prompt(text_chunk, config):
    num_questions = config.get('num_questions', 5)
    question_type = config.get('question_type', 'MCQ')
    num_options = config.get('num_options', 4)
    include_answers = config.get('include_answers', True)
    include_explanations = config.get('include_explanations', True)

    prompt = f"""
You are an expert educator and quiz generator. Your task is to generate a quiz based strictly on the provided text.

TEXT TO BASE QUIZ ON:
{text_chunk}

REQUIREMENTS:
- Generate exactly {num_questions} questions.
- Question type: {question_type}
"""
    
    if question_type == 'MCQ':
        prompt += f"- Each question must have exactly {num_options} distinct options.\n"
    
    prompt += """
- Return ONLY valid JSON and nothing else. No markdown framing (like ```json), no intro, no outro.
- Ensure the JSON conforms exactly to the following structure:
{
  "questions": [
    {
      "question": "string",
"""

    if question_type == 'MCQ':
        prompt += '      "options": ["string", "string", ...],\n'
    
    prompt += '      "answer": "string"'

    if include_explanations:
        prompt += ',\n      "explanation": "string"'

    prompt += """
    }
  ]
}
"""
    return prompt.strip()
