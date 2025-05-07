from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from engine import transcribe
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import httpx

app = FastAPI()
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
TRANSCRIBER_DB_URL = os.environ['TRANSCRIBER_DB_URL']
USER_SERVICE_URL = os.environ['USER_SERVICE_URL']

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    user_id: int = None,
    conversation_id: int = None
):
    if not user_id or not conversation_id:
        return {"error": "user_id and conversation_id are required"}
    
    # Verify user exists via user service
    async with httpx.AsyncClient() as client:
        user_response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        if user_response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()
        
        transcription = transcribe(temp_file.name)
        
        # Store in transcriber's database
        async with httpx.AsyncClient() as client:
            await client.post(f"{TRANSCRIBER_DB_URL}/transcriptions", json={
                "user_id": user_id,
                "conversation_id": conversation_id,
                "text": transcription
            })
        
        os.unlink(temp_file.name)
        
        return {"transcription": transcription}

@app.websocket("/ws/{user_id}/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, conversation_id: int):
    await websocket.accept()
    try:
        while True:
            audio_data = await websocket.receive_bytes()
            # Process audio data and store transcription
            # Similar to above but with streaming
    except:
        await websocket.close()
