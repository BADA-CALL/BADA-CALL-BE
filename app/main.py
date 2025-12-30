from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx
from datetime import datetime
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

@app.get("/keep-alive")
async def keep_alive():
    """서버 활성 상태 유지용 엔드포인트"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "message": "서버가 활성 상태입니다"
    }

# 백그라운드에서 자동으로 keep-alive 요청을 보내는 스케줄러
async def auto_ping():
    """14분마다 자동으로 keep-alive 요청"""
    while True:
        await asyncio.sleep(14 * 60)  # 14분 대기
        try:
            # 자신에게 ping 요청 (Render 환경에서는 외부 URL 사용)
            async with httpx.AsyncClient() as client:
                await client.get("https://badaback-api.onrender.com/keep-alive", timeout=30)
        except Exception as e:
            print(f"Auto ping failed: {e}")

@app.on_event("startup")
async def startup_event():
    """앱 시작시 백그라운드 태스크 시작"""
    asyncio.create_task(auto_ping())