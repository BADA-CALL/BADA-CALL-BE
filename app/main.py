from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, reports, locations

app = FastAPI(
    title="바다콜 Backend",
    description="바다 한가운데에서 사고 발생 시 GPS 기반 자동 사고 감지 및 긴급 신고 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(locations.router)

@app.get("/")
async def root():
    return {"message": "바다콜 Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}