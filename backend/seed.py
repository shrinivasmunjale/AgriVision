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

        # -----------------------------
        # Diseases
        # -----------------------------
        diseases = [
            Disease(
                id=2,
                name="Early Blight",
                description="A fungal disease caused by Alternaria solani affecting tomato plants",
                symptoms="Dark brown spots with concentric rings on older leaves, yellowing and leaf drop",
                causes="Warm humid weather, poor air circulation, overhead watering",
                severity_level="Medium"
            ),
            Disease(
                id=3,
                name="Late Blight",
                description="A devastating disease caused by Phytophthora infestans",
                symptoms="Water-soaked lesions on leaves and stems, white mold growth, rapid plant death",
                causes="Cool moist weather, spores spread by wind and rain",
                severity_level="High"
            ),
            Disease(
                id=4,
                name="Bacterial Spot",
                description="Bacterial disease caused by Xanthomonas species",
                symptoms="Small dark spots on leaves and fruit, yellow halos around spots",
                causes="Warm wet conditions, contaminated seeds or transplants",
                severity_level="Medium"
            ),
            Disease(
                id=5,
                name="Tomato Mosaic Virus",
                description="Viral disease causing mosaic pattern on leaves",
                symptoms="Mottled light and dark green leaf pattern, stunted growth, reduced yield",
                causes="Transmitted by handling infected plants, contaminated tools",
                severity_level="High"
            )
        ]
        
        db.add_all(diseases)
        await db.commit()
        print("✅ Diseases seeded successfully")

        # -----------------------------
        # Pesticides
        # -----------------------------
        pesticides = [
            Pesticide(
                id=1,
                name="Copper Fungicide",
                active_ingredient="Copper hydroxide",
                dosage="2-4 tablespoons per gallon",
                application_method="Foliar spray every 7-10 days"
            ),
            Pesticide(
                id=2,
                name="Chlorothalonil",
                active_ingredient="Chlorothalonil 75%",
                dosage="2 tablespoons per gallon",
                application_method="Spray foliage thoroughly every 7-14 days"
            ),
            Pesticide(
                id=3,
                name="Mancozeb",
                active_ingredient="Mancozeb 75% WP",
                dosage="2.5 tablespoons per gallon",
                application_method="Apply as protective spray before disease appears"
            ),
            Pesticide(
                id=4,
                name="Bacillus subtilis",
                active_ingredient="Bacillus subtilis strain",
                dosage="1-2 teaspoons per gallon",
                application_method="Spray every 7-14 days as preventative"
            ),
        ]
        
        db.add_all(pesticides)
        await db.commit()
        print("✅ Pesticides seeded successfully")

        # -----------------------------
        # Fertilizers
        # -----------------------------
        fertilizers = [
            Fertilizer(
                id=1,
                name="NPK 10-10-10",
                composition="Nitrogen 10%, Phosphorus 10%, Potassium 10%",
                dosage="1-2 tablespoons per plant every 2-3 weeks",
                application_stage="Vegetative and flowering stage"
            ),
            Fertilizer(
                id=2,
                name="Calcium Nitrate",
                composition="Calcium 19%, Nitrogen 15.5%",
                dosage="1 tablespoon per gallon water, apply as foliar spray",
                application_stage="During fruit development"
            ),
            Fertilizer(
                id=3,
                name="Fish Emulsion",
                composition="Nitrogen 5%, Phosphorus 2%, Potassium 2%",
                dosage="2-3 tablespoons per gallon, apply every 2 weeks",
                application_stage="Throughout growing season"
            ),
        ]
        
        db.add_all(fertilizers)
        await db.commit()
        print("✅ Fertilizers seeded successfully")

        print("🎉 Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())