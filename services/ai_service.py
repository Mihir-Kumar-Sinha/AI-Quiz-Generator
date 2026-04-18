import os
import requests
import json
import re
import time

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Ordered list of free models to try as fallbacks
FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "google/gemma-3-12b-it:free",
    "qwen/qwen3-coder:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
]

def call_openrouter(prompt, model=None):
    """Call OpenRouter API with automatic model fallback on 429 rate-limit errors."""
    
    if model and model not in FREE_MODELS:
        models_to_try = [model] + FREE_MODELS
    else:
        models_to_try = list(FREE_MODELS)

    last_error = None
    
    for current_model in models_to_try:
        print(f"Trying model: {current_model}", flush=True)
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "AI Quiz Generator"
        }
        
        payload = {
            "model": current_model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            
            # Check for rate-limit or payment errors BEFORE raise_for_status
            if response.status_code == 429:
                print(f"Rate limited (429) on model {current_model}, trying next...", flush=True)
                last_error = f"Rate limited on {current_model}"
                time.sleep(2)
                continue
            
            if response.status_code == 402:
                print(f"Payment required (402) on model {current_model}, trying next...", flush=True)
                last_error = f"Payment required on {current_model}"
                continue
            
            response.raise_for_status()
            
            result_json = response.json()
            if 'choices' in result_json and len(result_json['choices']) > 0:
                content = result_json['choices'][0]['message']['content']
                print(f"Success with model: {current_model}", flush=True)
                return extract_json_from_response(content)
            else:
                print(f"Unexpected API response structure: {result_json}", flush=True)
                return {"error": f"Unexpected API response: {json.dumps(result_json)}"}
                
        except requests.exceptions.Timeout:
            print(f"Timeout on model {current_model}, trying next...", flush=True)
            last_error = f"Timeout on {current_model}"
            continue
        except requests.exceptions.RequestException as e:
            error_msg = f"API Request failed: {e}"
            print(error_msg, flush=True)
            return {"error": error_msg}
    
    # All models exhausted
    error_msg = "All free AI models are currently rate-limited. Please wait a minute and try again."
    print(error_msg, flush=True)
    return {"error": error_msg}

def extract_json_from_response(content):
    print(f"Raw content from AI: {content}", flush=True)
    # Sometimes models return JSON with markdown headers or extra text
    try:
        # First attempt: parse directly
        return json.loads(content)
    except json.JSONDecodeError:
        pass
        
    try:
        # Second attempt: strip markdown JSON block
        if "```json" in content:
            block = content.split("```json")[1].split("```")[0].strip()
            return json.loads(block)
        elif "```" in content:
            block = content.split("```")[1].split("```")[0].strip()
            return json.loads(block)
    except (json.JSONDecodeError, IndexError):
        pass
        
    # Third attempt: regex to find { ... }
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"Regex JSON extraction failed: {e}", flush=True)
        
    print("Failed to find valid JSON in the model's response.", flush=True)
    return {"error": "Failed to parse JSON", "raw": content}
