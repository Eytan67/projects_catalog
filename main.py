from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from app.api.endpoints.progects import router as projects_router
from app.api.endpoints.admin import router as admin_router
from app.db.database import Base, engine

app = FastAPI(title="Projects Catalog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Create uploads directory for mock S3
uploads_dir = "/app/uploads"
os.makedirs(uploads_dir, exist_ok=True)

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

@app.get("/", response_class=JSONResponse)
async def root():
    return {"message": "Hello, world!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)