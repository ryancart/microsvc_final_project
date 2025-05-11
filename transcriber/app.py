from flask import Flask, request, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
from engine import transcribe
import subprocess
import sys
from collections import deque
from threading import Thread
import time

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')
audio_buffer = deque(maxlen=30) # 5 min 

users = []
conversations = []


def transcription_worker():
    cycle = 0
    while True:
        if cycle == 0 or cycle % 1000 == 0:
            print("transcription thread alive", file=sys.stderr)
        cycle += 1
        
        if len(audio_buffer) >= 30:
            print(f"[transcriber] buffer has {len(audio_buffer)} chunks", file=sys.stderr)
            try:
                slice = [audio_buffer.popleft() for _ in range(30)]
                raw_audio = b"".join(slice)
                text = transcribe(raw_audio)
                print(f"[rolling-transcribe] {text}", file=sys.stderr)
                socketio.emit("transcription", {
                    "text": text,
                    "speaker": users[0] if users else "unknown",
                    "timestamp": time.time()
                    })
            except Exception as e:
                print(f"[transcribe ERROR] {e}", file=sys.stderr)
        else:
            time.sleep(1)


@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    print(f"[socket] got chunk {len(data)} bytes", file=sys.stderr)
    audio_buffer.append(data)


@app.route('/start', methods=['GET'])
def start():
    user = request.args.get("user", "")
    conversation = request.args.get("conv", "")
    users.append(user)
    conversations.append(conversation)
    print(users[0], file=sys.stderr)
    print(conversations[0], file=sys.stderr)
    return redirect(url_for('get_transcriber', name=user, conversation=conversation))

    
@app.route('/get_transcriber', methods=['GET', 'POST'])
def get_transcriber():
        return render_template("get_transcriber.html")

Thread(target=transcription_worker, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8002, debug=True)
else:
    Thread(target=transcription_worker, daemon=True).start()

