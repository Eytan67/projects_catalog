from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.endpoints.progects import router as projects_router
from app.db.database import Base, engine

app = FastAPI(title="Projects Catalog API")

Base.metadata.create_all(bind=engine)

app.include_router(projects_router)

@app.get("/", response_class=JSONResponse)
async def root():
    return {"message": "Hello, world!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)