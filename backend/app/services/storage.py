import os
import uuid
from pathlib import Path
from typing import Optional
try:
    import aioboto3
    AIOBOTO3_AVAILABLE = True
except ImportError:
    AIOBOTO3_AVAILABLE = False

from app.core.config import settings

class R2StorageClient:
    def __init__(self):
        self.use_local = not AIOBOTO3_AVAILABLE or not settings.R2_ENDPOINT_URL
        
        if self.use_local:
            # Use local storage
            self.local_storage_path = Path("uploads")
            self.local_storage_path.mkdir(exist_ok=True)
        else:
            # Use R2
            self.session = aioboto3.Session()
            self.endpoint_url = settings.R2_ENDPOINT_URL
            self.bucket_name = settings.R2_BUCKET_NAME
            self.access_key = settings.R2_ACCESS_KEY
            self.secret_key = settings.R2_SECRET_KEY

    async def upload_file(self, file_data: bytes, filename: str, content_type: str = "image/jpeg") -> str:
        """Upload file to R2 or local storage and return URL"""
        # Generate unique filename
        ext = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{ext}"
        
        if self.use_local:
            # Save locally
            file_path = self.local_storage_path / unique_filename
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Get backend URL from settings
            backend_url = settings.BACKEND_URL
            
            # Return full URL with backend host
            return f"{backend_url}/uploads/{unique_filename}"
        else:
            # Upload to R2
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name='auto'
            ) as s3:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=unique_filename,
                    Body=file_data,
                    ContentType=content_type
                )
                
                # Return public URL
                return f"{self.endpoint_url}/{self.bucket_name}/{unique_filename}"
    
    async def delete_file(self, file_url: str):
        """Delete file from R2 or local storage"""
        if self.use_local:
            # Delete locally
            filename = file_url.split('/')[-1]
            file_path = self.local_storage_path / filename
            if file_path.exists():
                file_path.unlink()
        else:
            # Delete from R2
            filename = file_url.split('/')[-1]
            
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name='auto'
            ) as s3:
                await s3.delete_object(
                    Bucket=self.bucket_name,
                    Key=filename
                )

storage_client = R2StorageClient()
