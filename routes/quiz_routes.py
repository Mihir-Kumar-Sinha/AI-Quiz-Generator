from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from utils.file_extractor import extract_text
from services.quiz_service import generate_quiz

import uuid

quiz_bp = Blueprint('quiz_bp', __name__)

UPLOAD_FOLDER = '/tmp'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@quiz_bp.route('/process-input', methods=['POST'])
def process_input():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        try:
            text = extract_text(file_path, filename)
            # Remove the file after extraction
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"text": text}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400

@quiz_bp.route('/generate-quiz', methods=['POST'])
def handle_generate_quiz():
    data = request.json
    text = data.get('text', '')
    
    if not text or len(text.strip()) == 0:
        return jsonify({"error": "No text provided"}), 400
        
    config = {
        'num_questions': data.get('numQs', 5),
        'question_type': data.get('qType', 'MCQ'),
        'num_options': data.get('numOpts', 4),
        'include_answers': data.get('incAns', True),
        'include_explanations': data.get('incExp', True),
        'model': data.get('model', 'meta-llama/llama-3.3-70b-instruct:free')
    }
    
    try:
        quiz = generate_quiz(text, config)
        return jsonify(quiz), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
