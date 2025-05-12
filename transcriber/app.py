from flask import Flask, request, render_template, redirect, url_for
from gevent import monkey
monkey.patch_all()
from flask_socketio import SocketIO, emit
from engine import transcribe
import sys
from collections import deque
from threading import Thread, Lock
import time


app = Flask(__name__)
app.debug = True
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')

audio_buffer = deque(maxlen=10) # maxlen * 15s
buffer_lock = Lock()
users = []
conversations = []

thread_started = False


def transcription_worker():
    cycle = 0
    while True:        
        if cycle == 0 or cycle % 100 == 0:
            print("transcription thread alive", file=sys.stderr)
        cycle += 1
        buffer_len = len(audio_buffer)
        print(f"[transcriber] current buffer size: {buffer_len}", file=sys.stderr)
        
        with buffer_lock:
            if len(audio_buffer) >= 1:
                print(f"[transcriber] buffer has {len(audio_buffer)} chunks", file=sys.stderr)
                try:
                    slice = [audio_buffer.popleft() for _ in range(1)]
                except IndexError:
                    print("buffer pop not working", file=sys.stderr)
                    slice = []
            else:
                slice = []
        if not slice:
            socketio.sleep(1)
            continue
        try:
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
            
            
@socketio.on('connect')
def on_connect():
    print("[transcriber] client connected", file=sys.stderr)
    
    global thread_started
    if not thread_started:
        print("[transcriber] launching transcription thread", file=sys.stderr)
        Thread(target=transcription_worker, daemon=True).start()
        thread_started = True


@socketio.on("disconnect")
def on_disconnect():
    print("[transcriber] client disconnected", file=sys.stderr)

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    print(f"[socket] got chunk {len(data)} bytes", file=sys.stderr)
    with buffer_lock:
        audio_buffer.append(data)


@app.route('/start', methods=['GET'])
def start():
    user = request.args.get("user", "")
    conversation = request.args.get("conv", "")
    users.append(user)
    conversations.append(conversation)
    print(users[0], file=sys.stderr)
    print(conversations[0], file=sys.stderr)
    return redirect(url_for('get_transcriber', name=users[0], conversation=conversations[0]))

    
@app.route('/get_transcriber', methods=['GET', 'POST'])
def get_transcriber():
    return render_template("get_transcriber.html")


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8002, debug=True)

