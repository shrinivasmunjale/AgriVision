import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter()

SYSTEM_PROMPT = (
    "You are AgriBot, the helpful assistant of the AgriVision AI platform, which detects "
    "tomato leaf diseases from photos using machine learning. Answer concisely and helpfully "
    "about crop health, tomato diseases, their symptoms, causes, prevention, treatment, "
    "pesticides, fertilizers, and general farming best practices. If you don't know, say so plainly."
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list = []


@router.post("")
async def chat(request: ChatRequest):
    """Proxy a chat message to the configured AI provider."""
    if not settings.AI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI assistant is not configured. Add AI_API_KEY (and AI_PROVIDER/AI_MODEL) to the backend .env file.",
        )

    provider = (settings.AI_PROVIDER or "openai").strip().lower()
    model = settings.AI_MODEL or ("gpt-4o-mini" if provider == "openai" else "gemini-1.5-flash")
    history = request.history or []

    try:
        if provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {settings.AI_API_KEY}"}
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}]
                + history
                + [{"role": "user", "content": request.message}],
            }
            async with httpx.AsyncClient(timeout=40) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
            reply = data["choices"][0]["message"]["content"]

        else:  # gemini
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={settings.AI_API_KEY}"
            )
            payload = {
                "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser: {request.message}"}]}]
            }
            async with httpx.AsyncClient(timeout=40) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
            try:
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError):
                reply = "Sorry, I couldn't generate a response. Please try again."

        return {"reply": reply.strip()}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"AI provider returned an error: {e.response.status_code}")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Could not reach the AI provider: {e}")