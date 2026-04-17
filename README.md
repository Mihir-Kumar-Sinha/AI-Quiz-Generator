# AI Quiz Generator 🧠

A full-stack, AI-powered quiz generator that transforms raw text and documents into interactive quizzes instantly. Built with Python Flask, Vanilla JS, and OpenRouter API. Perfect for students and educators!

## Features 🚀

- **Smart Uploads**: Supports copy-pasting text, or uploading `.pdf`, `.docx`, and `.txt` files directly.
- **Micro-Chunking Logic**: Flawlessly processes large documents to create accurate context.
- **Interactive Quizzes**: Beautiful, glassmorphism-styled Multiple Choice and Q/A cards that provide answers + explanations.
- **Customizable**: Tweak the number of questions, question types, and option density natively.
- **Serverless Ready**: Engineered specifically to deploy securely on Vercel out-of-the-box.

## Tech Stack 🛠️

- **Frontend**: HTML5, Vanilla CSS (Glassmorphism & Micro-animations), Vanilla JavaScript.
- **Backend**: Python, Flask, `pdfplumber`, `python-docx`.
- **AI Integration**: OpenRouter API.

## Getting Started Locally 💻

1. Clone the repository to your local machine.
2. Create your virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your internal environment variable by creating a `.env` file at the root:
   ```env
   OPENROUTER_API_KEY=your_key_here
   ```
4. Start the application!
   ```bash
   python app.py
   ```
5. Navigate to `http://localhost:5000` in your browser.

## Deployment 🌐

This project is structured for 1-click deployment on Vercel! 
Simply push to GitHub, import the repository into your Vercel Dashboard, and ensure you link your `OPENROUTER_API_KEY` under the Environment Variables section. `vercel.json` will automatically construct the runtime.

---
_Aesthetically engineered and designed for seamless usage._
