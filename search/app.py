from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI()
SEARCH_DB_URL = os.environ['SEARCH_DB_URL']
TRANSCRIBER_SERVICE_URL = os.environ['TRANSCRIBER_SERVICE_URL']
USER_SERVICE_URL = os.environ['USER_SERVICE_URL']

@app.get("/search")
async def search(conversation_id: int):
    async with httpx.AsyncClient() as client:
        transcriptions = await client.get(
            f"{TRANSCRIBER_SERVICE_URL}/transcriptions",
            params={"conversation_id": conversation_id}
        )
        
        # Get user details from user service
        user_ids = set(t["user_id"] for t in transcriptions.json())
        users = {}
        for user_id in user_ids:
            user_response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
            users[user_id] = user_response.json()
        
        # Combine and order results
        results = []
        for t in transcriptions.json():
            results.append({
                "user": users[t["user_id"]]["username"],
                "text": t["text"],
                "timestamp": t["timestamp"]
            })
        
        return {"conversation": sorted(results, key=lambda x: x["timestamp"])}
