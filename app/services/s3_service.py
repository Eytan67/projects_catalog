import boto3
import uuid
from typing import Optional
from fastapi import HTTPException, UploadFile
from botocore.exceptions import ClientError, NoCredentialsError
from PIL import Image
import io

from app.core.config import settings

class S3Service:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.S3_BUCKET_NAME
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize S3 client only when needed"""
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            print("Warning: AWS credentials not configured. S3 functionality will be disabled.")
            return
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        except Exception as e:
            print(f"Warning: Failed to initialize S3 client: {str(e)}")
    
    def _ensure_s3_client(self):
        """Ensure S3 client is available for operations"""
        if not self.s3_client:
            raise HTTPException(
                status_code=500,
                detail="AWS S3 not configured. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
            )

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
        """Upload image to S3 and return the URL"""
        try:
            # Ensure S3 client is available
            self._ensure_s3_client()
            
            # Validate the image
            self.validate_image(file)
            
            # Read file content
            file_content = await file.read()
            
            # Resize image
            resized_content = self.resize_image(file_content)
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
            unique_filename = f"projects/{project_id or 'temp'}/{uuid.uuid4()}.{file_extension}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=resized_content,
                ContentType='image/jpeg',
                CacheControl='max-age=31536000',  # 1 year cache
                Metadata={
                    'original_filename': file.filename or 'unknown',
                    'project_id': project_id or 'temp'
                }
            )
            
            # Return the S3 URL
            return f"{settings.S3_BASE_URL}/{unique_filename}"
            
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image to S3: {str(e)}"
            )
        except NoCredentialsError:
            raise HTTPException(
                status_code=500,
                detail="AWS credentials not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during upload: {str(e)}"
            )

    def delete_image(self, image_url: str) -> bool:
        """Delete image from S3 using the URL"""
        try:
            # Check if S3 is configured
            if not self.s3_client:
                print("Warning: S3 not configured, cannot delete image")
                return False
            
            # Extract key from URL
            if not image_url.startswith(settings.S3_BASE_URL):
                return False
            
            key = image_url.replace(f"{settings.S3_BASE_URL}/", "")
            
            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            print(f"Error deleting image from S3: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error deleting image: {str(e)}")
            return False

# Create a singleton instance
s3_service = S3Service()