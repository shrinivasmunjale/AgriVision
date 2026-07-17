import asyncio
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.user import User
from app.models.disease import Disease
from app.models.pesticide import Pesticide
from app.models.fertilizer import Fertilizer
from app.core.security import get_password_hash


async def seed_data():
    async with SessionLocal() as db:
        print("🌱 Seeding database...")

        # -----------------------------
        # Skip if already seeded
        # -----------------------------
        result = await db.execute(select(User))
        existing_user = result.scalars().first()

        if existing_user:
            print("✅ Database already seeded.")
            return

        # -----------------------------
        # Admin User
        # -----------------------------
        admin = User(
            id="admin-uid-12345",
            name="Admin Operator",
            email="admin@agrivision.ai",
            hashed_password=get_password_hash("admin123"),
            role="Admin",
            farm_name="AgriVision Labs",
            phone="+919876543210",
        )

        # -----------------------------
        # Farmer User
        # -----------------------------
        farmer = User(
            id="farmer-uid-67890",
            name="Ramesh Patil",
            email="ramesh@agrifarm.com",
            hashed_password=get_password_hash("farmer123"),
            role="Farmer",
            farm_name="Patil Tomato Estate",
            phone="+919876543211",
        )

        db.add_all([admin, farmer])
        await db.commit()

        print("✅ Users seeded successfully.")

        # ====================================================
        # KEEP YOUR EXISTING PESTICIDE, FERTILIZER,
        # DISEASE SEEDING CODE HERE
        # ====================================================

        print("🎉 Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())