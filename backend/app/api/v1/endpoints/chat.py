import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from app.core.config import settings
from app.services.recommendation import recommendation_engine

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


def generate_knowledge_fallback(message: str) -> str:
    """Generate intelligent fallback answer using tomato_disease_knowledge.json"""
    msg_lower = message.lower()

    # Search knowledge dataset for matching disease
    if hasattr(recommendation_engine, 'knowledge_data') and recommendation_engine.knowledge_data:
        for item in recommendation_engine.knowledge_data:
            disease_name = item.get("disease", "")
            d_clean = disease_name.lower().replace("tomato", "").strip()

            if d_clean and (d_clean in msg_lower or disease_name.lower() in msg_lower):
                scientific = item.get("scientific_name", "")
                symptoms = ", ".join(item.get("symptoms", []))
                organic = ", ".join(item.get("organic_control", []))
                preventive = ", ".join(item.get("preventive_measures", []))

                pesticides = []
                for p in item.get("recommended_pesticides", []):
                    if isinstance(p, dict) and p.get("name"):
                        pesticides.append(f"{p['name']} ({p.get('dosage', 'follow product label')})")
                    elif isinstance(p, str):
                        pesticides.append(p)

                pesticide_str = "; ".join(pesticides) if pesticides else "Consult local agricultural extension."

                return (
                    f"🌿 **{disease_name}** ({scientific})\n\n"
                    f"• **Symptoms**: {symptoms or 'Dark leaf spots, wilting, or yellowing.'}\n"
                    f"• **Organic Control**: {organic or 'Improve air circulation, remove infected leaves, use neem oil.'}\n"
                    f"• **Preventive Measures**: {preventive or 'Use disease-free seedlings and practice crop rotation.'}\n"
                    f"• **Chemical Treatment**: {pesticide_str}"
                )

    if "fertilizer" in msg_lower or "npk" in msg_lower or "nutrition" in msg_lower:
        return (
            "🌱 **Tomato Fertilizer Guide**:\n\n"
            "• **Seedling Stage**: High Phosphorus (e.g., 10-52-10 or DAP) to establish strong roots.\n"
            "• **Vegetative Stage**: Balanced NPK (19-19-19) for lush leaf and stem development.\n"
            "• **Fruiting & Flowering**: High Potassium & Calcium (13-0-45, Calcium Nitrate) to prevent blossom end rot and improve yield."
        )

    if "pesticide" in msg_lower or "spray" in msg_lower or "fungicide" in msg_lower:
        return (
            "🛡️ **Crop Protection Advice**:\n\n"
            "• **Fungal Blights (Early/Late)**: Copper Hydroxide, Chlorothalonil, or Mancozeb.\n"
            "• **Bacterial Spot**: Copper Oxychloride sprays.\n"
            "• **Pests (Spider Mites)**: Neem Oil spray, Abamectin, or Insecticidal Soap.\n"
            "• Always wear PPE and observe pre-harvest intervals."
        )

    return (
        "🌱 **AgriBot Assistant**:\n\n"
        "I am here to help you manage your tomato crops! Ask me about:\n"
        "1. Crop diseases (e.g., *Early Blight*, *Bacterial Spot*, *Late Blight*)\n"
        "2. Organic treatments & preventive steps\n"
        "3. Recommended fertilizers & chemical spray schedules"
    )


@router.post("")
async def chat(request: ChatRequest):
    """Proxy a chat message to AI provider with knowledge base fallback."""
    if not settings.AI_API_KEY:
        return {"reply": generate_knowledge_fallback(request.message)}

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
            async with httpx.AsyncClient(timeout=15) as client:
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
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
            try:
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError):
                reply = generate_knowledge_fallback(request.message)

        return {"reply": reply.strip()}

    except Exception as e:
        print(f"[CHAT] Provider Error ({e}). Serving knowledge fallback.")
        return {"reply": generate_knowledge_fallback(request.message)}