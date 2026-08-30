import asyncio
import io
from pathlib import Path
from PIL import Image, ImageDraw

from app.ml.yolo_detector import yolo_detector
from app.services.pdf_report import pdf_generator

async def test_yolo_bounding_box_flow():
    print("[TEST] Creating synthetic test leaf image...")
    # Create sample synthetic leaf image (300x300, green background with brownish spot)
    img = Image.new("RGB", (300, 300), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw leaf (green ellipse)
    draw.ellipse([50, 40, 250, 260], fill=(40, 160, 60))
    # Draw disease spot (brown spot on leaf)
    draw.ellipse([110, 100, 170, 160], fill=(160, 80, 20))
    draw.ellipse([140, 150, 190, 200], fill=(140, 70, 15))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    raw_bytes = img_bytes.getvalue()

    print("[TEST] Running YOLO annotation on test image...")
    annotated_bytes, boxes = await yolo_detector.annotate_image(
        image_input=raw_bytes,
        disease_name="Early Blight",
        confidence=0.89
    )

    output_path = Path("uploads") / "test_yolo_bbox_output.jpg"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(annotated_bytes)
    print(f"[SUCCESS] Annotated image saved to: {output_path} (Detected {len(boxes)} boxes)")

    print("[TEST] Testing PDF Report Generation with YOLO Bounding Box image...")
    prediction_data = {
        "confidence_score": 0.89,
        "created_at": "August 30, 2026 08:15 PM",
        "image_url": str(output_path),
        "annotated_image_url": str(output_path)
    }
    user_data = {"name": "Test Farmer", "farm_name": "AgriVision Test Farm", "email": "test@agrivision.ai"}
    disease_data = {
        "name": "Early Blight",
        "description": "Fungal disease caused by Alternaria solani.",
        "symptoms": "Dark brown spots with concentric rings on leaves.",
        "causes": "High humidity and warm temperatures.",
        "severity_level": "Moderate"
    }
    recommendations = [
        {"pesticide_name": "Mancozeb 75% WP", "dosage": "2g per liter", "similarity_score": 0.92}
    ]

    pdf_buffer = pdf_generator.generate_report(
        prediction_data=prediction_data,
        user_data=user_data,
        disease_data=disease_data,
        recommendations=recommendations
    )

    pdf_path = Path("uploads") / "test_yolo_report.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_buffer.getvalue())
    print(f"[SUCCESS] PDF report generated and saved to: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(test_yolo_bounding_box_flow())
