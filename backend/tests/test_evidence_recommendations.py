import unittest
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.v1.endpoints.recommendations import (

    model_class_for_name,
    EXACT_MODEL_CLASSES,
    serialize_recommendation,
)
from app.models.evidence_recommendation import DiseaseRecommendation


class TestEvidenceRecommendations(unittest.TestCase):
    def test_exact_model_class_mapping_preserves_efficienet_names(self):
        self.assertEqual(model_class_for_name("Early Blight"), "Tomato___Early_blight")
        self.assertEqual(model_class_for_name("Tomato Early Blight"), "Tomato___Early_blight")
        self.assertEqual(model_class_for_name("Tomato___Target_Spot"), "Tomato___Target_Spot")
        self.assertEqual(model_class_for_name("Target Spot"), "Tomato___Target_Spot")
        self.assertEqual(model_class_for_name("Healthy"), "Tomato___healthy")
        self.assertEqual(model_class_for_name("Tomato Healthy"), "Tomato___healthy")
        self.assertEqual(model_class_for_name("Spider Mites (Two-Spotted)"), "Tomato___Spider_mites Two-spotted_spider_mite")
        self.assertEqual(model_class_for_name("Two-Spotted Spider Mite"), "Tomato___Spider_mites Two-spotted_spider_mite")

    def test_all_10_efficientnet_classes_in_set(self):
        expected_classes = {
            "Tomato___Bacterial_spot",
            "Tomato___Early_blight",
            "Tomato___Late_blight",
            "Tomato___Leaf_Mold",
            "Tomato___Septoria_leaf_spot",
            "Tomato___Spider_mites Two-spotted_spider_mite",
            "Tomato___Target_Spot",
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
            "Tomato___Tomato_mosaic_virus",
            "Tomato___healthy",
        }
        self.assertEqual(EXACT_MODEL_CLASSES, expected_classes)

    def test_unknown_disease_does_not_create_a_recommendation_class(self):
        self.assertIsNone(model_class_for_name("Invented Unknown Wheat Rust"))
        self.assertIsNone(model_class_for_name(""))
        self.assertIsNone(model_class_for_name(None))

    def test_viral_classes_are_mapped_correctly(self):
        self.assertEqual(model_class_for_name("Tomato Mosaic Virus"), "Tomato___Tomato_mosaic_virus")
        self.assertEqual(model_class_for_name("Tomato Yellow Leaf Curl Virus"), "Tomato___Tomato_Yellow_Leaf_Curl_Virus")
        self.assertEqual(model_class_for_name("TYLCV"), "Tomato___Tomato_Yellow_Leaf_Curl_Virus")

    def test_recommendation_serialization_contains_source_provenance(self):
        rec = DiseaseRecommendation(
            id=1,
            model_class="Tomato___Early_blight",
            display_name="Early Blight",
            recommendation_type="Fungicide",
            active_ingredient="Copper Oxychloride",
            dose="3",
            dose_unit="g/L",
            application_method="Foliar spray",
            source_organization="ICAR",
            source_type="Government Agricultural Advisory",
            source_document="ICAR Kharif Agro-Advisory 2025",
            source_url="https://www.icar.gov.in/sites/default/files/2025-10/ICAR-En-Kharif-Agro-Advisories-for-Farmers-2025.pdf",
            evidence_note="ICAR advisory lists Copper Oxychloride at 3 g/L for management of early blight.",
            verified_date=date(2026, 9, 22),
            is_active=True,
        )
        serialized = serialize_recommendation(rec)
        self.assertEqual(serialized["id"], 1)
        self.assertEqual(serialized["active_ingredient"], "Copper Oxychloride")
        self.assertEqual(serialized["dose"], "3")
        self.assertEqual(serialized["dose_unit"], "g/L")
        self.assertEqual(serialized["source"]["organization"], "ICAR")
        self.assertEqual(serialized["source"]["source_type"], "Government Agricultural Advisory")
        self.assertTrue(serialized["source"]["url"].startswith("https://"))


from app.api.v1.endpoints.fertilizer_recommendations import (
    serialize_fertilizer_rec,
    format_application_schedule,
)
from app.models.evidence_recommendation import FertilizerRecommendation


class TestFertilizerRecommendations(unittest.TestCase):
    def test_mpkv_hybrid_fertilizer_serialization(self):
        rec = FertilizerRecommendation(
            id=1,
            crop="Tomato",
            variety_type="Hybrid",
            crop_stage="Transplanting",
            soil_test_required=False,
            nitrogen_kg_ha=300.0,
            phosphorus_kg_ha=150.0,
            potassium_kg_ha=150.0,
            fym_tonne_ha=20.0,
            recommendation="Apply FYM @ 20 t/ha and N:P₂O₅:K₂O @ 300:150:150 kg/ha for hybrid tomato.",
            application_schedule="Full FYM + 50% N + full P + full K at transplanting. Remaining 50% N in 3 equal split applications at 20-day intervals.",
            application_method="Basal application and top dressing splits",
            source_organization="Mahatma Phule Krishi Vidyapeeth (MPKV), Rahuri",
            source_type="Agricultural University Research Recommendation",
            source_document="AICRP on Vegetables - Research Recommendations",
            source_url="https://mpkv.ac.in/Uploads/Research/33.%20AICRP%20on%20Vegetables_20250926041136.pdf",
            evidence_level="AGRICULTURAL_UNIVERSITY",
            verified_date=date(2026, 9, 22),
            is_active=True,
        )
        serialized = serialize_fertilizer_rec(rec)
        self.assertEqual(serialized["crop"], "Tomato")
        self.assertEqual(serialized["variety_type"], "Hybrid")
        self.assertEqual(serialized["nutrients"]["nitrogen"]["value"], 300.0)
        self.assertEqual(serialized["nutrients"]["phosphorus"]["value"], 150.0)
        self.assertEqual(serialized["nutrients"]["potassium"]["value"], 150.0)
        self.assertEqual(serialized["nutrients"]["fym"]["value"], 20.0)
        self.assertEqual(serialized["source"]["organization"], "Mahatma Phule Krishi Vidyapeeth (MPKV), Rahuri")
        self.assertEqual(serialized["source"]["evidence_level"], "AGRICULTURAL_UNIVERSITY")
        self.assertTrue(len(serialized["application_schedule"]["transplanting"]) > 0)
        self.assertTrue("MPKV" in serialized["disclaimer"])


if __name__ == "__main__":
    unittest.main()

