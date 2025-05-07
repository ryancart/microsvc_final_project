import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)
API_URL = os.environ.get('API_URL', 'http://nginx')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form.get('username')
        if not username:
            return jsonify({"error": "Username is required"}), 400

        response = requests.post(
            f"{API_URL}/api/users",
            json={"username": username},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = e.response.json().get('detail', str(e)) if hasattr(e, 'response') else str(e)
        return jsonify({"error": error_msg}), 500

@app.route('/conversations', methods=['GET'])
def get_conversations():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        response = requests.get(f"{API_URL}/api/conversations", params={'user_id': user_id})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = e.response.json().get('detail', str(e)) if hasattr(e, 'response') else str(e)
        return jsonify({"error": error_msg}), 500

@app.route('/conversations', methods=['POST'])
def create_conversation():
    try:
        user_id = request.form.get('user_id')
        conversation_name = request.form.get('conversation_name')
        
        if not user_id or not conversation_name:
            return jsonify({"error": "User ID and conversation name are required"}), 400

        response = requests.post(
            f"{API_URL}/api/conversations",
            json={
                "name": conversation_name,
                "user_id": int(user_id)
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = e.response.json().get('detail', str(e)) if hasattr(e, 'response') else str(e)
        return jsonify({"error": error_msg}), 500

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        user_id = request.form.get('user_id')
        conversation_id = request.form.get('conversation_id')

        if not user_id or not conversation_id:
            return jsonify({"error": "User ID and conversation ID are required"}), 400

        files = {'file': (file.filename, file.stream, file.content_type)}
        data = {
            'user_id': int(user_id),
            'conversation_id': conversation_id
        }

        response = requests.post(f"{API_URL}/api/transcribe", files=files, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = e.response.json().get('detail', str(e)) if hasattr(e, 'response') else str(e)
        return jsonify({"error": error_msg}), 500

@app.route('/do_search', methods=['GET'])
def do_search():
    try:
        conversation_id = request.args.get('conversation_id')
        resp = requests.get(f"{API_URL}/api/search", params={'conversation_id': conversation_id})
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
