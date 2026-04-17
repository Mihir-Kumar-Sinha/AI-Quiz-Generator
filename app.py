from flask import Flask
from dotenv import load_dotenv

import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    from routes.page_routes import page_bp
    from routes.quiz_routes import quiz_bp
    
    app.register_blueprint(page_bp)
    app.register_blueprint(quiz_bp, url_prefix='/api')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
