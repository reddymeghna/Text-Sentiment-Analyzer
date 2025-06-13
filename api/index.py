from flask import Flask, render_template, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__, template_folder="../templates")
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def analyze_sentiment(text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that gives sentiment (Positive/Negative/Neutral), confidence %, and explains why."},
            {"role": "user", "content": f"Analyze this text: '{text}'. Provide:\n1. Sentiment\n2. Confidence out of 100\n3. Explanation"}
        ]
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response_data = response.json()
        if "choices" in response_data:
            reply = response_data["choices"][0]["message"]["content"]
            lines = reply.split('\n')
            sentiment = lines[0].split(":")[-1].strip()
            confidence = lines[1].split(":")[-1].strip()
            explanation = '\n'.join(lines[2:]).strip()
            return sentiment, confidence, explanation
        else:
            return "Error", "N/A", response_data.get("error", {}).get("message", "Unknown error.")
    except Exception as e:
        return "Error", "N/A", str(e)

@app.route("/", methods=["GET", "POST"])
def index():
    sentiment = confidence = explanation = None
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename.endswith(".txt"):
                text = file.read().decode("utf-8")
                sentiment, confidence, explanation = analyze_sentiment(text)
    return render_template("index.html", sentiment=sentiment, confidence=confidence, explanation=explanation)

# Required by Vercel
def handler(environ, start_response):
    return app(environ, start_response)



if __name__ == "__main__":
    app.run(debug=True)
