import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "projects-catalog-images")
    
    # File Upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # Mock S3 Toggle
    USE_MOCK_S3: bool = os.getenv("USE_MOCK_S3", "true").lower() == "true"
    
    @property
    def S3_BASE_URL(self) -> str:
        if self.USE_MOCK_S3:
            return "http://localhost:8000/uploads"
        return f"https://{self.S3_BUCKET_NAME}.s3.{self.AWS_REGION}.amazonaws.com"

settings = Settings()
