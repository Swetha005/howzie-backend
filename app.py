import os
import requests # type: ignore
from flask import Flask, request, jsonify # type: ignore
from bs4 import BeautifulSoup # type: ignore
from flask_cors import CORS # type: ignore

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Replace this with your actual API Key (as a string, not using os.getenv now)
GEMINI_API_KEY = "AIzaSyAjkj6UBahCeV0ZeV9vVIblzxJOUloGg0g"
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}'

def scrape_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"Scraping Error: {str(e)}"

def get_gemini_response(content, query):
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Given the following content:\n\n{content}\n\nAnswer the question: {query}"
                }]
            }]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Gemini Error: {str(e)}"

@app.route('/ask-query', methods=['POST'])
def ask_query():
    data = request.get_json()
    url = data.get('url')
    query = data.get('query')

    if not url or not query:
        return jsonify({"error": "URL and query are required."}), 400

    content = scrape_content(url)
    if "Error" in content:
        return jsonify({"error": content}), 500

    ai_response = get_gemini_response(content, query)
    return jsonify({"answer": ai_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))

