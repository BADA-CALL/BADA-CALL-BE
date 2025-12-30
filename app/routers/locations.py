from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models import (
    LocationUpdate,
    LocationResponse
)
# from app.auth import get_current_user  # 더 이상 필요 없음
import uuid
from app.database import supabase

router = APIRouter(prefix="/location", tags=["위치 관리"])

@router.post("/update", response_model=LocationResponse, summary="GPS 위치 업데이트")
async def update_location(
    location_data: LocationUpdate
):
    """
    사용자의 GPS 위치를 업데이트합니다.

    **인증이 필요하지 않은 엔드포인트입니다.**

    - **device_id**: 기기 고유 ID
    - **latitude**: 위도
    - **longitude**: 경도
    - **accuracy**: GPS 정확도 (미터, 선택사항)
    - **altitude**: 고도 (미터, 선택사항)
    - **speed**: 속도 (m/s, 선택사항)
    - **heading**: 방향 (도, 선택사항)
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 기기 ID로 사용자 확인 (선택적)
        user_response = supabase.table("users").select("id").eq("device_id", location_data.device_id).execute()
        user_id = user_response.data[0]["id"] if user_response.data else None

        # timestamp 처리
        if location_data.timestamp:
            if isinstance(location_data.timestamp, str):
                try:
                    # ISO 8601 형식 파싱
                    timestamp = datetime.fromisoformat(location_data.timestamp.replace('Z', '+00:00')).isoformat()
                except Exception:
                    timestamp = datetime.utcnow().isoformat()
            else:
                timestamp = location_data.timestamp.isoformat()
        else:
            timestamp = datetime.utcnow().isoformat()

        # 위치 데이터 준비
        location_insert_data = {
            "device_id": location_data.device_id,
            "user_id": user_id,
            "latitude": location_data.latitude,
            "longitude": location_data.longitude,
            "accuracy": location_data.accuracy,
            "altitude": location_data.altitude,
            "speed": location_data.speed,
            "heading": location_data.heading,
            "timestamp": timestamp
        }

        # 데이터베이스에 위치 저장
        response = supabase.table("locations").insert(location_insert_data).execute()

        if response.data:
            location = response.data[0]
            return LocationResponse(
                id=str(location["id"]),
                device_id=str(location["device_id"]),
                latitude=location["latitude"],
                longitude=location["longitude"],
                accuracy=location.get("accuracy"),
                altitude=location.get("altitude"),
                speed=location.get("speed"),
                heading=location.get("heading"),
                timestamp=location["timestamp"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="위치 저장에 실패했습니다"
            )

    except Exception as e:
        print(f"Error updating location: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="위치 업데이트 중 오류가 발생했습니다"
        )

@router.get("/current", response_model=LocationResponse, summary="현재 위치 조회")
async def get_current_location(
    device_id: str
):
    """
    사용자의 최신 위치를 조회합니다.
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 최신 위치 조회 (시간순 정렬)
        response = supabase.table("locations")\
            .select("*")\
            .eq("device_id", device_id)\
            .order("timestamp", desc=True)\
            .limit(1)\
            .execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="위치 정보를 찾을 수 없습니다"
            )

        location = response.data[0]
        return LocationResponse(
            id=str(location["id"]),
            device_id=str(location["device_id"]),
            latitude=location["latitude"],
            longitude=location["longitude"],
            accuracy=location.get("accuracy"),
            altitude=location.get("altitude"),
            speed=location.get("speed"),
            heading=location.get("heading"),
            timestamp=location["timestamp"]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching current location: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="현재 위치 조회 중 오류가 발생했습니다"
        )

@router.get("/history", response_model=List[LocationResponse], summary="위치 이력 조회")
async def get_location_history(
    device_id: str,
    limit: int = Query(default=20, ge=1, le=100, description="조회할 개수 (1-100)"),
    offset: int = Query(default=0, ge=0, description="건너뛸 개수")
):
    """
    사용자의 위치 이력을 조회합니다.

    - **limit**: 조회할 개수 (기본값: 20, 최대: 100)
    - **offset**: 건너뛸 개수 (기본값: 0)
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 위치 이력 조회 (최신순)
        response = supabase.table("locations")\
            .select("*")\
            .eq("device_id", device_id)\
            .order("timestamp", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        locations = []
        for location in response.data:
            locations.append(LocationResponse(
                id=str(location["id"]),
                device_id=str(location["device_id"]),
                latitude=location["latitude"],
                longitude=location["longitude"],
                accuracy=location.get("accuracy"),
                altitude=location.get("altitude"),
                speed=location.get("speed"),
                heading=location.get("heading"),
                timestamp=location["timestamp"]
            ))

        return locations

    except Exception as e:
        print(f"Error fetching location history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="위치 이력 조회 중 오류가 발생했습니다"
        )

@router.get("/stats", summary="위치 통계")
async def get_location_stats(
    device_id: str
):
    """
    사용자의 위치 통계 정보를 조회합니다.

    - 총 위치 기록 수
    - 첫 기록 시간
    - 마지막 기록 시간
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 통계 조회
        response = supabase.table("locations")\
            .select("id, timestamp")\
            .eq("device_id", device_id)\
            .order("timestamp", desc=False)\
            .execute()

        total_count = len(response.data)

        if total_count == 0:
            return {
                "total_count": 0,
                "first_record": None,
                "last_record": None
            }

        first_record = response.data[0]["timestamp"]
        last_record = response.data[-1]["timestamp"]

        return {
            "total_count": total_count,
            "first_record": first_record,
            "last_record": last_record
        }

    except Exception as e:
        print(f"Error fetching location stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="위치 통계 조회 중 오류가 발생했습니다"
        )