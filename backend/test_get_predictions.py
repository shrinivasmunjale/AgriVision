import requests

# Login first
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "farmer@example.com",
        "password": "farmer123"
    }
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✓ Login successful")
    
    # Get predictions
    headers = {'Authorization': f'Bearer {token}'}
    predictions_response = requests.get(
        "http://localhost:8000/api/v1/predictions",
        headers=headers,
        params={"limit": 5}
    )
    
    print(f"\nGET /predictions Status: {predictions_response.status_code}")
    
    if predictions_response.status_code == 200:
        predictions = predictions_response.json()
        print(f"✓ Found {len(predictions)} predictions\n")
        
        for i, pred in enumerate(predictions, 1):
            print(f"{i}. ID: {pred['id']}")
            print(f"   Disease: {pred.get('disease_name', 'Unknown')}")
            print(f"   Confidence: {pred['confidence_score']*100:.1f}%")
            print(f"   Image URL: {pred['image_url']}")
            print(f"   Recommendations: {len(pred.get('recommendations', []))}")
            print()
    else:
        print(f"✗ Error: {predictions_response.text}")
else:
    print(f"✗ Login failed: {login_response.text}")
