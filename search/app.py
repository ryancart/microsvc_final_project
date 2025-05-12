from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime

app = Flask(__name__)

DATABASE_URL = "http://database:8004/transcriptions"

@app.route("/search", methods=["GET"])
def search_conversation():
    conversation_name = request.args.get("conversation")
    if not conversation_name:
        return render_template("search.html")  # no query yet

    try:
        response = requests.get(DATABASE_URL, timeout=5)
        response.raise_for_status()
        all_transcripts = response.json()
    except Exception as e:
        return render_template("search.html", error=f"Failed to query database: {e}")

    filtered = [
        t for t in all_transcripts
        if t.get("conversation_name") == conversation_name
    ]
    filtered.sort(key=lambda t: t.get("created_at", ""))

    formatted = [
        f"{t['first_name']} {t['last_name']} said: {t['text']}"
        for t in filtered
    ]

    return render_template(
        "search.html",
        conversation_name=conversation_name,
        conversation=formatted
    )
    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8003)
