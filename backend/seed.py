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
        # Test Users
        # -----------------------------
        farmer = User(
            id="farmer-test-id",
            name="Test Farmer",
            email="farmer@test.com",
            hashed_password=get_password_hash("password123"),
            role="farmer",
            farm_name="Test Farm",
            phone="+911234567890",
        )

        admin = User(
            id="admin-test-id",
            name="Test Admin",
            email="admin@test.com",
            hashed_password=get_password_hash("password123"),
            role="admin",
            farm_name="AgriVision",
            phone="+919876543210",
        )

        expert = User(
            id="expert-test-id",
            name="Test Expert",
            email="expert@test.com",
            hashed_password=get_password_hash("password123"),
            role="expert",
            farm_name="AgriVision",
            phone="+919876543211",
        )

        db.add_all([farmer, admin, expert])
        await db.commit()

        print("✅ Test users seeded successfully:")
        print("   - farmer@test.com / password123")
        print("   - admin@test.com / password123")
        print("   - expert@test.com / password123")

        # ====================================================
        # KEEP YOUR EXISTING PESTICIDE, FERTILIZER,
        # DISEASE SEEDING CODE HERE
        # ====================================================

        print("🎉 Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())