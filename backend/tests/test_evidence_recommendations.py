from app.api.v1.endpoints.recommendations import model_class_for_name


def test_exact_model_class_mapping_preserves_efficienet_names():
    assert model_class_for_name("Early Blight") == "Tomato___Early_blight"
    assert model_class_for_name("Tomato___Target_Spot") == "Tomato___Target_Spot"
    assert model_class_for_name("Healthy") == "Tomato___healthy"


def test_unknown_disease_does_not_create_a_recommendation_class():
    assert model_class_for_name("Invented Disease") is None


def test_viral_classes_are_not_mapped_to_fungicide_names():
    assert model_class_for_name("Tomato Mosaic Virus") == "Tomato___Tomato_mosaic_virus"
    assert model_class_for_name("Tomato Yellow Leaf Curl Virus") == "Tomato___Tomato_Yellow_Leaf_Curl_Virus"
