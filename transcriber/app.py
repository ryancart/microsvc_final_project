from flask import Flask, request, render_template, redirect, url_for
from gevent import monkey
monkey.patch_all()
from flask_socketio import SocketIO, emit
from engine import transcribe
import sys
from collections import deque
from threading import Thread, Lock
import time
import queue
import threading
import requests
from datetime import datetime, timezone

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')

record_queue = queue.Queue()
audio_buffer = deque(maxlen=10) # maxlen * 15s
buffer_lock = Lock()
# users = []
# conversations = []
user_sessions = {}

transcribe_thread_started = False
write2db_thread_started = False


def transcription_worker():
    cycle = 0
    while True:        
        if cycle == 0 or cycle % 10 == 0:
            print("transcription thread alive", file=sys.stderr)
            buffer_len = len(audio_buffer)
            print(f"[transcriber] current buffer size: {buffer_len}", file=sys.stderr)
            
        cycle += 1
        
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
            
            sid = next(iter(socketio.server.manager.get_participants('/', '/')), None)
            user_info = user_sessions.get(sid, {
                "first_name": "unknown",
                "last_name": "unknown",
                "conversation": "unknown"
            })

            socketio.emit("transcription", {
                "text": text,
                "speaker": f"{user_info['first_name']} {user_info['last_name']}",
                "timestamp": time.time()
            })

            record = {
                "first_name":        user_info["first_name"],
                "last_name":         user_info["last_name"],
                "conversation_name": user_info["conversation"],
                "text":              text,
                "created_at":        datetime.now(timezone.utc).isoformat()
            }
            record_queue.put(record)
        except Exception as e:
            print(f"[transcribe ERROR] {e}", file=sys.stderr)
    
            
def db_worker():
    while True:
        rec = record_queue.get()
        try:
            requests.post(
                "http://database:8004/transcriptions",
                json=rec,
                timeout=5
            )
        except Exception as e:
            print(f"[DB ERROR] {e}")
        finally:
            record_queue.task_done()          
            
            
@socketio.on('connect')
def on_connect():
    sid = request.sid
    print(f"[transcriber] client connected: {sid}", file=sys.stderr)
    
    global transcribe_thread_started
    global write2db_thread_started
    
    environ = request.environ
    if "pending_user" in environ:
        user_sessions[sid] = environ["pending_user"]
        print(f"[transcriber] bound user to sid {sid}", file=sys.stderr)
    
    if not transcribe_thread_started:
        print("[transcriber] launching transcription thread", file=sys.stderr)
        Thread(target=transcription_worker, daemon=True).start()
        transcribe_thread_started = True
        
    if not write2db_thread_started:
        print("[transcriber] launching write2db thread", file=sys.stderr)
        threading.Thread(target=db_worker, daemon=True).start()
        write2db_thread_started = True


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
    # user = request.args.get("user", "")
    user_str = request.args.get("user", "").strip()
    parts = user_str.split(' ', 1)
    first_name = parts[0]
    last_name  = parts[1] if len(parts) > 1 else ""
    conversation = request.args.get("conv", "")
    request.environ["pending_user"] = {
        "first_name": first_name,
        "last_name":  last_name,
        "conversation": conversation
    }

    print(f"First: {first_name!r}, Last: {last_name!r}", file=sys.stderr)
    print(conversation, file=sys.stderr)
    return redirect(url_for('get_transcriber', name=first_name, conversation=conversation))


@app.route('/get_transcriber', methods=['GET', 'POST'])
def get_transcriber():
    return render_template("get_transcriber.html")


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8002, debug=True)

