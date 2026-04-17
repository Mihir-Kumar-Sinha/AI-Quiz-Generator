import os
import requests
import json
import re

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter(prompt, model="google/gemma-3-12b-it:free"):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "AI Quiz Generator"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result_json = response.json()
        if 'choices' in result_json and len(result_json['choices']) > 0:
            content = result_json['choices'][0]['message']['content']
            return extract_json_from_response(content)
        else:
            print(f"Unexpected API response structure: {result_json}", flush=True)
            return {"error": f"Unexpected API response: {json.dumps(result_json)}"}
            
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else None
        if status_code == 429:
            error_msg = "API Rate Limit Exceeded (429). The OpenRouter API key has run out of requests or credits. Please wait or try a different key."
        elif status_code == 402:
            error_msg = "Payment Required (402). The OpenRouter API key has run out of credits for this model."
        else:
            error_msg = f"API Request failed: {e.response.text if e.response else e}"
        print(error_msg, flush=True)
        return {"error": error_msg}
    except requests.exceptions.RequestException as e:
        error_msg = f"API Request failed: {e}"
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
