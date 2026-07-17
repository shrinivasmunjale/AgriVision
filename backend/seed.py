import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal, engine
from app.models.user import User
from app.models.disease import Disease
from app.models.pesticide import Pesticide
from app.models.fertilizer import Fertilizer

async def seed_data():
    async with SessionLocal() as db:
        print("Seeding database...")

        # 1. Create Users
        admin = User(
            id="admin-uid-12345",
            name="Admin Operator",
            email="admin@agrivision.ai",
            role="Admin",
            farm_name="AgriVision Labs",
            phone="+919876543210"
        )
        farmer = User(
            id="farmer-uid-67890",
            name="Ramesh Patil",
            email="ramesh@agrifarm.com",
            role="Farmer",
            farm_name="Patil Tomato Estate",
            phone="+919876543211"
        )
        db.add_all([admin, farmer])
        await db.commit()
        print("Users seeded.")

        # 2. Create Pesticides
        p1 = Pesticide(
            name="Copper Octanoate Fungicide",
            active_ingredient="Copper Octanoate (Soap)",
            dosage="2.0 fl oz / gallon of water",
            application_method="Spray foliage thoroughly at first sign of infection. Repeat every 7-10 days until dry weather returns."
        )
        p2 = Pesticide(
            name="Chlorothalonil 720 SFT",
            active_ingredient="Chlorothalonil",
            dosage="1.5 tbsp / gallon of water",
            application_method="Apply on a 7-day schedule to foliage. Ensure coverage of both upper and lower leaf surfaces."
        )
        p3 = Pesticide(
            name="Imidacloprid Systemic Insecticide",
            active_ingredient="Imidacloprid",
            dosage="0.5 fl oz / gallon of water",
            application_method="Apply as foliar spray or soil drench to target whiteflies and aphids that act as viral vectors."
        )
        db.add_all([p1, p2, p3])
        await db.commit()
        print("Pesticides seeded.")

        # 3. Create Fertilizers
        f1 = Fertilizer(
            name="Soluble Tomato Feed 4-18-38",
            composition="NPK 4-18-38 with Magnesium and Micronutrients",
            dosage="1.0 gram / gallon of water",
            application_stage="Apply weekly at root zone once first blossom clusters set fruit."
        )
        f2 = Fertilizer(
            name="Calcium Nitrate Greenhouse Grade",
            composition="Calcium (Ca) 19%, Nitrogen (N) 15.5%",
            dosage="1.5 grams / gallon of water",
            application_stage="Apply at blossom set and early fruit expansion to boost cell wall strength and prevent blossom end rot."
        )
        f3 = Fertilizer(
            name="Balanced Bio-Organic Grow",
            composition="NPK 5-5-5 Organic Blend",
            dosage="2 cups per plant root zone",
            application_stage="Mix thoroughly into soil surface around transplanting or early vegetative growth."
        )
        db.add_all([f1, f2, f3])
        await db.commit()
        print("Fertilizers seeded.")

        # 4. Create Diseases and Link Treatments
        d_healthy = Disease(
            name="Healthy",
            description="The tomato leaves show no visible signs of fungal, bacterial, or viral disease. Photosynthesis efficiency is optimal.",
            symptoms="Uniform deep green leaf color. Smooth edges. No spot blemishes, yellow margins, or wilted tissue.",
            causes="Correct watering, balanced soil nutrition, and effective pest management controls.",
            severity_level="Low",
            reference_image_url="https://images.unsplash.com/photo-1592417817098-8f3d6eb19675"
        )
        d_healthy.fertilizers.append(f3)

        d_early_blight = Disease(
            name="Early Blight",
            description="A common fungal disease caused by Alternaria solani. It targets older foliage first and thrives in warm, humid conditions.",
            symptoms="Dark brown spots with concentric rings (target-like pattern) starting on lower leaves. Leaves yellow and drop off.",
            causes="Fungal spores overwintering in soil debris, spread by rain splash and high humidity.",
            severity_level="Medium",
            reference_image_url="https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2"
        )
        d_early_blight.pesticides.extend([p1, p2])
        d_early_blight.fertilizers.append(f2) # Calcium helps prevent structural decay

        d_late_blight = Disease(
            name="Late Blight",
            description="A destructive fungal-like oomycete disease caused by Phytophthora infestans. Can kill plants rapidly in cool, wet weather.",
            symptoms="Large, water-soaked dark lesions on leaves and stems. A white, fuzzy mold growth appears on leaf undersides in humid weather.",
            causes="Oomycete spores carried by wind currents and splashing rain in persistently damp, cool weather.",
            severity_level="High",
            reference_image_url="https://images.unsplash.com/photo-1599420186946-7b6fb4e297f0"
        )
        d_late_blight.pesticides.extend([p1, p2])
        d_late_blight.fertilizers.append(f1)

        d_bacterial_spot = Disease(
            name="Bacterial Spot",
            description="Caused by Xanthomonas campestris. Affects leaves, stems, and fruit, particularly during warm, rainy seasons.",
            symptoms="Small, water-soaked circular greasy spots on leaves. Centers of spots may dry out and crack, giving a shot-hole appearance.",
            causes="Bacterial entry through stomata or mechanical wounds, spread via overhead irrigation or rain.",
            severity_level="Medium",
            reference_image_url="https://images.unsplash.com/photo-1560807707-8cc77767d783"
        )
        d_bacterial_spot.pesticides.append(p1) # Copper is effective against bacteria

        d_mosaic_virus = Disease(
            name="Tomato Mosaic Virus",
            description="A highly infectious viral pathogen (ToMV). Causes stunting and mottling, reducing yield quality and crop weight.",
            symptoms="Light and dark green mosaic patterns on leaves. Leaves may become narrow, puckered, or fern-like ('shoestring' symptom).",
            causes="Mechanical transmission from tools/hands, and aphid vector transmissions.",
            severity_level="High",
            reference_image_url="https://images.unsplash.com/photo-1589156280159-27698a70f29e"
        )
        d_mosaic_virus.pesticides.append(p3) # Target insect vectors
        d_mosaic_virus.fertilizers.extend([f1, f3]) # Boost plant immunity with balanced feed

        db.add_all([d_healthy, d_early_blight, d_late_blight, d_bacterial_spot, d_mosaic_virus])
        await db.commit()
        print("Diseases and associations seeded.")
        print("Database seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
