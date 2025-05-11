from fastapi import FastAPI, HTTPException
from typing import List
import requests
import datetime

app = FastAPI()
USER_SVC = "http://user-service:8001"
TRANSCRIBE_BASE = "http://{user}-transcriber:8002"

@app.get("/api/search")
def search(conversation: str):
    # 1) get participants
    r = requests.get(f"{USER_SVC}/api/conversations")
    # Suppose we store conv→participants mapping; stub here
    participants = [1,2]  # replace with real lookup
    # 2) collect all transcripts
    all_entries = []
    for u in participants:
        r2 = requests.get(f"{TRANSCRIBE_BASE.format(user=u)}/api/transcriptions", params={"conversation": conversation})
        if r2.status_code != 200:
            continue
        for e in r2.json():
            all_entries.append(e)
    # 3) sort by timestamp
    all_entries.sort(key=lambda x: datetime.datetime.fromisoformat(x["timestamp"]))
    return all_entries




# from fastapi import FastAPI, HTTPException
# import httpx
# import os

# app = FastAPI()
# SEARCH_DB_URL = os.environ['SEARCH_DB_URL']
# TRANSCRIBER_SERVICE_URL = os.environ['TRANSCRIBER_SERVICE_URL']
# USER_SERVICE_URL = os.environ['USER_SERVICE_URL']

# @app.get("/search")
# async def search(conversation_id: str):
#     try:
#         async with httpx.AsyncClient() as client:
#             # Get transcriptions
#             transcriptions_response = await client.get(
#                 f"{TRANSCRIBER_SERVICE_URL}/transcriptions",
#                 params={"conversation_id": conversation_id}
#             )
            
#             if transcriptions_response.status_code == 404:
#                 return {"conversation": []}
            
#             transcriptions_response.raise_for_status()
#             transcriptions = transcriptions_response.json()
            
#             if not transcriptions:
#                 return {"conversation": []}
            
#             # Get user details
#             user_ids = set(t["user_id"] for t in transcriptions)
#             users = {}
#             for user_id in user_ids:
#                 user_response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
#                 user_response.raise_for_status()
#                 users[user_id] = user_response.json()
            
#             # Combine and order results
#             results = []
#             for t in transcriptions:
#                 results.append({
#                     "user": users[t["user_id"]]["username"],
#                     "text": t["text"],
#                     "timestamp": t["timestamp"]
#                 })
            
#             return {"conversation": sorted(results, key=lambda x: x["timestamp"])}
#     except httpx.RequestError as e:
#         raise HTTPException(status_code=500, detail=f"Service communication error: {str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
