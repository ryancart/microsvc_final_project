from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI()
SEARCH_DB_URL = os.environ['SEARCH_DB_URL']
TRANSCRIBER_SERVICE_URL = os.environ['TRANSCRIBER_SERVICE_URL']
USER_SERVICE_URL = os.environ['USER_SERVICE_URL']

@app.get("/search")
async def search(conversation_id: str):
    try:
        async with httpx.AsyncClient() as client:
            # Get transcriptions
            transcriptions_response = await client.get(
                f"{TRANSCRIBER_SERVICE_URL}/transcriptions",
                params={"conversation_id": conversation_id}
            )
            
            if transcriptions_response.status_code == 404:
                return {"conversation": []}
            
            transcriptions_response.raise_for_status()
            transcriptions = transcriptions_response.json()
            
            if not transcriptions:
                return {"conversation": []}
            
            # Get user details
            user_ids = set(t["user_id"] for t in transcriptions)
            users = {}
            for user_id in user_ids:
                user_response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
                user_response.raise_for_status()
                users[user_id] = user_response.json()
            
            # Combine and order results
            results = []
            for t in transcriptions:
                results.append({
                    "user": users[t["user_id"]]["username"],
                    "text": t["text"],
                    "timestamp": t["timestamp"]
                })
            
            return {"conversation": sorted(results, key=lambda x: x["timestamp"])}
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Service communication error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
