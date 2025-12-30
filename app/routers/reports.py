from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import (
    EmergencyReportCreate,
    AutoDetectionReport,
    ReportUpdate,
    ReportResponse,
    ReportStatus
)
# from app.auth import get_current_user  # 더 이상 필요 없음
from app.database import supabase

router = APIRouter(prefix="/reports", tags=["신고 관리"])

@router.post("/emergency", response_model=ReportResponse, summary="긴급 신고")
async def create_emergency_report(
    report_data: EmergencyReportCreate,
    device_id: str
):
    """
    긴급 신고를 접수합니다.

    - **type**: 신고 유형 (manual/auto_detection)
    - **emergency_type**: 사고 종류 (collision, fire, medical_emergency 등)
    - **location_latitude**: 위도
    - **location_longitude**: 경도
    - **location_address**: 주소 (선택사항)
    - **description**: 상황 설명 (선택사항)
    - **sensor_data**: 센서 데이터 (선택사항)
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 신고 데이터 준비
        report_insert_data = {
            "user_id": current_user["id"],
            "type": report_data.type,
            "status": ReportStatus.PENDING,
            "location_latitude": report_data.location_latitude,
            "location_longitude": report_data.location_longitude,
            "location_address": report_data.location_address,
            "description": report_data.description,
            "sensor_data": report_data.sensor_data,
            "reported_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        # 데이터베이스에 신고 생성
        response = supabase.table("reports").insert(report_insert_data).execute()

        if response.data:
            report = response.data[0]
            return ReportResponse(
                id=str(report["id"]),
                device_id=str(report["device_id"]),
                type=report["type"],
                status=report["status"],
                location_latitude=report["location_latitude"],
                location_longitude=report["location_longitude"],
                location_address=report.get("location_address"),
                sensor_data=report.get("sensor_data"),
                accident_probability=report.get("accident_probability"),
                voice_file_url=report.get("voice_file_url"),
                video_file_url=report.get("video_file_url"),
                description=report.get("description"),
                reported_at=report["reported_at"],
                updated_at=report["updated_at"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="신고 접수에 실패했습니다"
            )

    except Exception as e:
        print(f"Error creating emergency report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="신고 처리 중 오류가 발생했습니다"
        )

@router.post("/auto-detection", response_model=ReportResponse, summary="자동 사고 감지 신고")
async def create_auto_detection_report(
    report_data: AutoDetectionReport
):
    """
    자동 사고 감지 신고를 접수합니다.

    **인증이 필요하지 않은 엔드포인트입니다.**

    - **device_id**: 기기 고유 ID
    - **location_latitude**: 위도
    - **location_longitude**: 경도
    - **sensor_data**: 센서 데이터 (가속도, 충격 등)
    - **accident_probability**: 사고 확률 (0.0 ~ 1.0)
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 기기 ID로 사용자 확인
        user_response = supabase.table("users").select("id").eq("device_id", report_data.device_id).execute()
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록되지 않은 기기입니다. 먼저 온보딩을 완료해주세요."
            )

        user_id = user_response.data[0]["id"]

        # 자동 감지 신고 데이터 준비
        report_id = str(uuid.uuid4())
        report_insert_data = {
            "id": report_id,
            "device_id": report_data.device_id,
            "user_id": user_id,
            "type": report_data.type,
            "status": ReportStatus.PENDING,
            "location_latitude": report_data.location_latitude,
            "location_longitude": report_data.location_longitude,
            "sensor_data": report_data.sensor_data,
            "accident_probability": report_data.accident_probability,
            "reported_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        # 데이터베이스에 신고 생성
        response = supabase.table("reports").insert(report_insert_data).execute()

        if response.data:
            report = response.data[0]
            return ReportResponse(
                id=str(report["id"]),
                device_id=str(report["device_id"]),
                type=report["type"],
                status=report["status"],
                location_latitude=report["location_latitude"],
                location_longitude=report["location_longitude"],
                location_address=report.get("location_address"),
                sensor_data=report.get("sensor_data"),
                accident_probability=report.get("accident_probability"),
                voice_file_url=report.get("voice_file_url"),
                video_file_url=report.get("video_file_url"),
                description=report.get("description"),
                reported_at=report["reported_at"],
                updated_at=report["updated_at"]
            )

    except Exception as e:
        print(f"Error creating auto detection report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="자동 감지 신고 처리 중 오류가 발생했습니다"
        )

@router.get("/status/{report_id}", response_model=ReportResponse, summary="신고 상태 조회")
async def get_report_status(
    report_id: str,
    device_id: str
):
    """
    특정 신고의 상태를 조회합니다.

    - **report_id**: 신고 ID (UUID)
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 신고 조회 (사용자 본인의 신고만)
        response = supabase.table("reports").select("*").eq("id", report_id).eq("user_id", current_user["id"]).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="신고를 찾을 수 없습니다"
            )

        report = response.data[0]
        return ReportResponse(
            id=str(report["id"]),
            device_id=str(report["device_id"]),
            type=report["type"],
            status=report["status"],
            location_latitude=report["location_latitude"],
            location_longitude=report["location_longitude"],
            location_address=report.get("location_address"),
            sensor_data=report.get("sensor_data"),
            accident_probability=report.get("accident_probability"),
            voice_file_url=report.get("voice_file_url"),
            video_file_url=report.get("video_file_url"),
            description=report.get("description"),
            reported_at=report["reported_at"],
            updated_at=report["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching report status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="신고 상태 조회 중 오류가 발생했습니다"
        )

@router.put("/{report_id}/cancel", response_model=ReportResponse, summary="신고 취소")
async def cancel_report(
    report_id: str,
    device_id: str
):
    """
    신고를 취소합니다. (PENDING 상태에서만 가능)

    - **report_id**: 신고 ID (UUID)
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 먼저 신고 존재 여부 및 상태 확인
        response = supabase.table("reports").select("*").eq("id", report_id).eq("user_id", current_user["id"]).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="신고를 찾을 수 없습니다"
            )

        report = response.data[0]

        # PENDING 상태에서만 취소 가능
        if report["status"] != ReportStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="접수 중인 신고만 취소할 수 있습니다"
            )

        # 상태를 CANCELLED로 업데이트
        update_response = supabase.table("reports").update({
            "status": ReportStatus.CANCELLED,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", report_id).eq("user_id", current_user["id"]).execute()

        if update_response.data:
            updated_report = update_response.data[0]
            return ReportResponse(
                id=str(updated_report["id"]),
                user_id=str(updated_report["user_id"]),
                type=updated_report["type"],
                status=updated_report["status"],
                location_latitude=updated_report["location_latitude"],
                location_longitude=updated_report["location_longitude"],
                location_address=updated_report.get("location_address"),
                sensor_data=updated_report.get("sensor_data"),
                accident_probability=updated_report.get("accident_probability"),
                voice_file_url=updated_report.get("voice_file_url"),
                video_file_url=updated_report.get("video_file_url"),
                description=updated_report.get("description"),
                reported_at=updated_report["reported_at"],
                updated_at=updated_report["updated_at"]
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error cancelling report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="신고 취소 중 오류가 발생했습니다"
        )

@router.get("/history", response_model=List[ReportResponse], summary="신고 이력 조회")
async def get_report_history(
    device_id: str,
    limit: int = 10,
    offset: int = 0
):
    """
    사용자의 신고 이력을 조회합니다.

    - **limit**: 조회할 개수 (기본값: 10)
    - **offset**: 건너뛸 개수 (기본값: 0)
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 사용자의 모든 신고 조회 (최신순)
        response = supabase.table("reports")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .order("reported_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        reports = []
        for report in response.data:
            reports.append(ReportResponse(
                id=str(report["id"]),
                device_id=str(report["device_id"]),
                type=report["type"],
                status=report["status"],
                location_latitude=report["location_latitude"],
                location_longitude=report["location_longitude"],
                location_address=report.get("location_address"),
                sensor_data=report.get("sensor_data"),
                accident_probability=report.get("accident_probability"),
                voice_file_url=report.get("voice_file_url"),
                video_file_url=report.get("video_file_url"),
                description=report.get("description"),
                reported_at=report["reported_at"],
                updated_at=report["updated_at"]
            ))

        return reports

    except Exception as e:
        print(f"Error fetching report history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="신고 이력 조회 중 오류가 발생했습니다"
        )