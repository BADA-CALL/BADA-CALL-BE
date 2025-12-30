from fastapi import APIRouter, HTTPException, status
from app.models import OnboardingData, OnboardingResponse, UserProfile, EmergencyContact
from app.database import supabase
from datetime import datetime
import uuid

router = APIRouter(prefix="/onboarding", tags=["온보딩"])

@router.post("/setup", response_model=OnboardingResponse, summary="온보딩 정보 설정")
async def setup_onboarding(onboarding_data: OnboardingData):
    """
    앱 최초 설치 시 사용자 정보를 설정합니다.

    **인증이 필요하지 않은 엔드포인트입니다.**

    - **device_id**: 앱에서 생성한 고유 기기 ID
    - **name**: 사용자 이름
    - **phone**: 전화번호
    - **boat_name**: 선박명 (선택사항)
    - **boat_number**: 선박번호 (선택사항)
    - **emergency_contact_***: 비상연락처 (선택사항)
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 기존 device_id 확인
        response = supabase.table("users").select("*").eq("device_id", onboarding_data.device_id).execute()
        if response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 기기입니다"
            )

        # 새 사용자 생성
        user_id = str(uuid.uuid4())
        user_insert_data = {
            "id": user_id,
            "device_id": onboarding_data.device_id,
            "name": onboarding_data.name,
            "phone": onboarding_data.phone,
            "boat_name": onboarding_data.boat_name,
            "boat_number": onboarding_data.boat_number,
            "created_at": datetime.utcnow().isoformat()
        }

        response = supabase.table("users").insert(user_insert_data).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 생성에 실패했습니다"
            )

        # 비상연락처 저장
        if onboarding_data.emergency_contact_1_name and onboarding_data.emergency_contact_1_phone:
            emergency_contact_1 = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": onboarding_data.emergency_contact_1_name,
                "phone": onboarding_data.emergency_contact_1_phone,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.table("emergency_contacts").insert(emergency_contact_1).execute()

        if onboarding_data.emergency_contact_2_name and onboarding_data.emergency_contact_2_phone:
            emergency_contact_2 = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": onboarding_data.emergency_contact_2_name,
                "phone": onboarding_data.emergency_contact_2_phone,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.table("emergency_contacts").insert(emergency_contact_2).execute()

        return OnboardingResponse(
            device_id=onboarding_data.device_id,
            message="온보딩 완료되었습니다",
            user_id=user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="온보딩 처리 중 오류가 발생했습니다"
        )

@router.get("/profile/{device_id}", response_model=UserProfile, summary="프로필 조회")
async def get_profile(device_id: str):
    """
    기기 ID로 사용자 프로필을 조회합니다.

    **인증이 필요하지 않은 엔드포인트입니다.**
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 사용자 정보 조회
        response = supabase.table("users").select("*").eq("device_id", device_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록되지 않은 기기입니다"
            )

        user = response.data[0]

        # 비상연락처 조회
        emergency_contacts_response = supabase.table("emergency_contacts").select("*").eq("user_id", user["id"]).execute()
        emergency_contacts = [
            EmergencyContact(name=contact["name"], phone=contact["phone"])
            for contact in emergency_contacts_response.data
        ]

        return UserProfile(
            device_id=user["device_id"],
            name=user["name"],
            phone=user["phone"],
            boat_name=user.get("boat_name"),
            boat_number=user.get("boat_number"),
            emergency_contacts=emergency_contacts,
            created_at=user["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 조회 중 오류가 발생했습니다"
        )

@router.put("/profile/{device_id}", response_model=UserProfile, summary="프로필 수정")
async def update_profile(device_id: str, profile_data: OnboardingData):
    """
    사용자 프로필을 수정합니다.

    **인증이 필요하지 않은 엔드포인트입니다.**
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다."
        )

    try:
        # 사용자 존재 확인
        response = supabase.table("users").select("id").eq("device_id", device_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록되지 않은 기기입니다"
            )

        user_id = response.data[0]["id"]

        # 사용자 정보 업데이트
        update_data = {
            "name": profile_data.name,
            "phone": profile_data.phone,
            "boat_name": profile_data.boat_name,
            "boat_number": profile_data.boat_number
        }

        supabase.table("users").update(update_data).eq("device_id", device_id).execute()

        # 기존 비상연락처 삭제
        supabase.table("emergency_contacts").delete().eq("user_id", user_id).execute()

        # 새 비상연락처 추가
        if profile_data.emergency_contact_1_name and profile_data.emergency_contact_1_phone:
            emergency_contact_1 = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": profile_data.emergency_contact_1_name,
                "phone": profile_data.emergency_contact_1_phone,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.table("emergency_contacts").insert(emergency_contact_1).execute()

        if profile_data.emergency_contact_2_name and profile_data.emergency_contact_2_phone:
            emergency_contact_2 = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": profile_data.emergency_contact_2_name,
                "phone": profile_data.emergency_contact_2_phone,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.table("emergency_contacts").insert(emergency_contact_2).execute()

        # 업데이트된 프로필 반환
        return await get_profile(device_id)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 수정 중 오류가 발생했습니다"
        )