import os
import uuid
from typing import Optional
from fastapi import HTTPException, UploadFile
from PIL import Image
import io

from app.core.config import settings

class MockS3Service:
    def __init__(self):
        self.base_dir = "/app/uploads"  # Local storage directory
        self.base_url = "http://localhost:8000/uploads"  # Mock URL base
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Ensure upload directory exists"""
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(f"{self.base_dir}/projects", exist_ok=True)

    def validate_image(self, file: UploadFile) -> None:
        """Validate uploaded image file"""
        # Check file size
        if hasattr(file, 'size') and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Check content type
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
            )

    def resize_image(self, image_data: bytes, max_size: tuple = (1024, 1024)) -> bytes:
        """Resize image to maximum dimensions while maintaining aspect ratio"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize image
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Error processing image: {str(e)}"
            )

    async def upload_image(self, file: UploadFile, project_id: Optional[str] = None) -> str:
        """Upload image to local storage and return the mock URL"""
        try:
            # Validate the image
            self.validate_image(file)
            
            # Read file content
            file_content = await file.read()
            
            # Resize image
            resized_content = self.resize_image(file_content)
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Create project directory if needed
            project_dir = f"{self.base_dir}/projects/{project_id or 'temp'}"
            os.makedirs(project_dir, exist_ok=True)
            
            # Save file locally
            file_path = f"{project_dir}/{unique_filename}"
            with open(file_path, 'wb') as f:
                f.write(resized_content)
            
            # Return the mock URL
            mock_url = f"{self.base_url}/projects/{project_id or 'temp'}/{unique_filename}"
            print(f"Mock S3: Uploaded image to {file_path}, URL: {mock_url}")
            return mock_url
            
        except Exception as e:
            print(f"Mock S3 upload error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image: {str(e)}"
            )

    def delete_image(self, image_url: str) -> bool:
        """Delete image from local storage using the URL"""
        try:
            # Extract path from URL
            if not image_url.startswith(self.base_url):
                return False
            
            relative_path = image_url.replace(f"{self.base_url}/", "")
            file_path = f"{self.base_dir}/{relative_path}"
            
            # Delete file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Mock S3: Deleted image {file_path}")
                return True
            else:
                print(f"Mock S3: File not found {file_path}")
                return False
                
        except Exception as e:
            print(f"Mock S3 delete error: {str(e)}")
            return False

# Create a singleton instance
mock_s3_service = MockS3Service()