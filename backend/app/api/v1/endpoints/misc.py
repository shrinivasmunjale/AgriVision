import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.models.contact import ContactMessage

router = APIRouter()

# ---------------- Weather ----------------
# Uses Open-Meteo (free, no API key required).


@router.get("/weather")
async def get_weather(lat: float = 0.0, lon: float = 0.0):
    """Return current weather + short forecast for farming context."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
        "timezone": "auto",
        "forecast_days": 5,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
    except (httpx.HTTPError, ValueError) as e:
        raise HTTPException(status_code=502, detail=f"Weather service unavailable: {e}")


# ---------------- Contact ----------------

class ContactRequest(BaseModel):
    name: str = ""
    email: EmailStr
    subject: str = ""
    message: str


@router.post("/contact")
async def submit_contact(
    contact: ContactRequest,
    db: AsyncSession = Depends(get_db),
):
    """Persist a contact form message."""
    if not contact.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    record = ContactMessage(
        name=contact.name,
        email=contact.email,
        subject=contact.subject,
        message=contact.message,
    )
    db.add(record)
    await db.commit()
    return {"message": "Thank you! Your message has been received."}


# ---------------- Farming tips ----------------

@router.get("/tips")
async def get_tips():
    """Return a curated list of farming tips."""
    tips = [
        "Rotate your crops every season to reduce soil-borne diseases.",
        "Water early in the morning to let foliage dry and reduce fungal growth.",
        "Remove and dispose of infected leaves immediately to stop spread.",
        "Space plants adequately to improve airflow and lower humidity.",
        "Use mulch to keep soil moisture stable and limit weed competition.",
        "Apply fertilizers based on soil tests rather than guesswork.",
        "Inspect your field weekly for early signs of pests and diseases.",
        "Choose disease-resistant tomato varieties for better resilience.",
        "Avoid overhead watering in the evening to prevent leaf wetness.",
        "Keep tools clean and sanitized between plants to avoid contamination.",
    ]
    return {"tips": tips}