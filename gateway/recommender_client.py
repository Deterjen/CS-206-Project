# recommender_client.py
import httpx

async def get_recommendations_from_flask(preferences: dict):
    async with httpx.AsyncClient() as client:
        flask_response = await client.post("http://flask-backend/recommend", json=preferences)
    
    if flask_response.status_code == 200:
        return flask_response.json()
    return None
