import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)
API = os.environ.get('API_URL', 'http://localhost')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    user_id = request.form['user_id']
    f = request.files['audio']
    files = {'file': (f.filename, f.stream, f.mimetype)}
    data = {'user_id': user_id}
    resp = requests.post(f"{API}/api/transcribe", data=data, files=files)
    return jsonify(resp.json())

@app.route('/do_search', methods=['GET'])
def do_search():
    user_id = request.args.get('user_id')
    resp = requests.get(f"{API}/api/search", params={'user_id': user_id})
    return jsonify(resp.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
