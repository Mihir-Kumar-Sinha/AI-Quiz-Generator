from utils.prompt_builder import build_quiz_prompt
from services.ai_service import call_openrouter

def generate_quiz(text, config):
    # A simple token-based chunking logic (rough estimate: 1 word ~ 1.3 tokens)
    # We will split text into chunks of about 1200 words
    words = text.split()
    chunk_size = 1200
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    
    # If the text is very large, maybe we only want to generate a certain total number of questions.
    # The simplest is to divide questions among chunks or just process the first few chunks.
    # We will distribute the requested questions roughly equally among chunks.
    
    total_questions = int(config.get('num_questions', 5))
    questions_per_chunk = max(1, total_questions // len(chunks))
    remainder = total_questions % len(chunks)
    
    all_questions = []
    
    for idx, chunk in enumerate(chunks[:5]): # process max 5 chunks to prevent abuse
        chunk_config = config.copy()
        q_count = questions_per_chunk + (1 if idx < remainder else 0)
        if q_count == 0:
            continue
            
        chunk_config['num_questions'] = q_count
        prompt = build_quiz_prompt(chunk, chunk_config)
        
        # We can specify model here if we want or just pass it in config
        model = config.get('model', 'meta-llama/llama-3.3-70b-instruct:free')
        
        chunk_response = call_openrouter(prompt, model=model)
        
        if chunk_response:
            if 'error' in chunk_response:
                raise Exception(chunk_response['error'])
            elif 'questions' in chunk_response:
                all_questions.extend(chunk_response['questions'])
            elif isinstance(chunk_response, dict):
                # Try to grab root if it's not nested
                for key, val in chunk_response.items():
                    if isinstance(val, list):
                        all_questions.extend(val)
                        break
                    
        # Stop early if we reached the required amount
        if len(all_questions) >= total_questions:
            break
            
    final_quiz = {
        "questions": all_questions[:total_questions]
    }
    
    return final_quiz
