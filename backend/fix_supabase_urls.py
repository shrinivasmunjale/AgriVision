import sys
import os
import asyncio
import urllib.request

# Add backend to path
sys.path.append(r"d:\AgriVision\backend")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.prediction import Prediction

def check_url(url: str) -> int:
    if not url.startswith("http://") and not url.startswith("https://"):
        return 0
    try:
        req = urllib.request.Request(
            url, 
            method='HEAD',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return 404

async def fix_urls():
    db_url = "postgresql+asyncpg://postgres.hpkxmferbjefrxltafek:Agrivision%40123@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres"
    
    engine = create_async_engine(db_url)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)
    
    print("Connecting to Supabase PostgreSQL database...")
    async with SessionLocal() as db:
        result = await db.execute(select(Prediction))
        predictions = result.scalars().all()
        print(f"Found {len(predictions)} total prediction records in Supabase.")
        
        updated_count = 0
        for pred in predictions:
            old_url = pred.image_url
            if "onrender.com" in old_url or old_url.startswith("http://localhost"):
                status = check_url(old_url)
                if status == 404:
                    print(f"Fixing broken URL for prediction {pred.id}: {old_url} -> /placeholder-leaf.png")
                    pred.image_url = "/placeholder-leaf.png"
                    updated_count += 1
                else:
                    print(f"URL {old_url} is valid (status: {status})")
            elif old_url == "/placeholder-leaf.png":
                print(f"Prediction {pred.id} already uses fallback /placeholder-leaf.png")
        
        if updated_count > 0:
            await db.commit()
            print(f"\n[SUCCESS] Successfully updated {updated_count} broken prediction image URLs in Supabase.")
        else:
            print("\n[INFO] No prediction image URLs required updating in Supabase.")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_urls())
