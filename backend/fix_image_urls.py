import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import SessionLocal
from app.models.prediction import Prediction

async def fix_image_urls():
    """Fix image URLs to use full backend URL"""
    async with SessionLocal() as db:
        # Get all predictions with relative URLs
        result = await db.execute(
            select(Prediction).filter(Prediction.image_url.like('/uploads/%'))
        )
        predictions = result.scalars().all()
        
        if not predictions:
            print("No predictions with relative URLs found")
            return
        
        print(f"Found {len(predictions)} predictions to fix")
        
        for pred in predictions:
            # Update to full URL
            old_url = pred.image_url
            pred.image_url = f"http://localhost:8000{old_url}"
            print(f"  Updated: {old_url} -> {pred.image_url}")
        
        await db.commit()
        print(f"\n✓ Fixed {len(predictions)} image URLs")

if __name__ == "__main__":
    print("Fixing image URLs in database...\n")
    asyncio.run(fix_image_urls())
