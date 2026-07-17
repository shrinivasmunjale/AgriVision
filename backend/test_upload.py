import requests
import io
from PIL import Image

# Create a simple test image
img = Image.new('RGB', (100, 100), color='red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_byte_arr.seek(0)

# First, login to get token
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "farmer@example.com",
        "password": "farmer123"
    }
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✓ Login successful, token: {token[:20]}...")
    
    # Now try to upload
    files = {'files': ('test.jpg', img_byte_arr, 'image/jpeg')}
    headers = {'Authorization': f'Bearer {token}'}
    
    upload_response = requests.post(
        "http://localhost:8000/api/v1/predictions/upload",
        files=files,
        headers=headers
    )
    
    print(f"\nUpload Status: {upload_response.status_code}")
    print(f"Upload Response: {upload_response.text}")
else:
    print(f"✗ Login failed: {login_response.text}")
