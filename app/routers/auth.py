from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from app.models import UserRegister, UserLogin, Token, User
from app.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_phone,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["인증"])

@router.post("/register", response_model=Token, summary="회원가입")
async def register(user_data: UserRegister):
    """
    새 사용자를 등록합니다.

    - **name**: 사용자 이름
    - **phone**: 전화번호 (로그인 ID로 사용)
    - **password**: 비밀번호
    - **boat_name**: 선박명 (선택사항)
    - **boat_number**: 선박번호 (선택사항)
    """
    # 기존 사용자 확인
    existing_user = await get_user_by_phone(user_data.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 전화번호입니다"
        )

    # 새 사용자 생성
    user = await create_user(user_data.dict())

    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user["id"])
    )

@router.post("/login", response_model=Token, summary="로그인")
async def login(user_credentials: UserLogin):
    """
    사용자 로그인을 처리합니다.

    - **phone**: 전화번호
    - **password**: 비밀번호
    """
    user = await authenticate_user(user_credentials.phone, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="전화번호 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user["id"])
    )

@router.get("/me", response_model=User, summary="내 정보 조회")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    현재 로그인된 사용자의 정보를 조회합니다.

    **인증이 필요한 엔드포인트입니다.**
    """
    return User(
        id=str(current_user["id"]),
        name=current_user["name"],
        phone=current_user["phone"],
        boat_name=current_user.get("boat_name"),
        boat_number=current_user.get("boat_number"),
        emergency_contacts=[],  # TODO: 비상연락처 조회 구현
        created_at=current_user["created_at"]
    )

@router.post("/refresh", response_model=Token, summary="토큰 갱신")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    JWT 토큰을 갱신합니다.

    **인증이 필요한 엔드포인트입니다.**
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user["id"])},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=str(current_user["id"])
    )