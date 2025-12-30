from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.models import TokenData, User
from app.database import supabase

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해시화"""
    # bcrypt는 72바이트 제한이 있으므로 길이 체크
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 유효하지 않습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_user_by_phone(phone: str) -> Optional[dict]:
    """전화번호로 사용자 조회"""
    if supabase is None:
        print("⚠️  Supabase 연결이 필요합니다")
        return None

    try:
        response = supabase.table("users").select("*").eq("phone", phone).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error fetching user by phone: {e}")
        return None

async def get_user_by_id(user_id: str) -> Optional[dict]:
    """사용자 ID로 사용자 조회"""
    if supabase is None:
        print("⚠️  Supabase 연결이 필요합니다")
        return None

    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error fetching user by id: {e}")
        return None

async def authenticate_user(phone: str, password: str) -> Optional[dict]:
    """사용자 인증"""
    user = await get_user_by_phone(phone)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """현재 사용자 조회 (의존성 주입)"""
    token = credentials.credentials
    token_data = verify_token(token)
    user = await get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def create_user(user_data: dict) -> dict:
    """새 사용자 생성"""
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결이 필요합니다. Supabase 설정을 확인해주세요."
        )

    try:
        # 비밀번호 해시화
        hashed_password = get_password_hash(user_data["password"])

        # 사용자 데이터 준비
        user_insert_data = {
            "name": user_data["name"],
            "phone": user_data["phone"],
            "password_hash": hashed_password,
            "boat_name": user_data.get("boat_name"),
            "boat_number": user_data.get("boat_number"),
            "created_at": datetime.utcnow().isoformat()
        }

        # 데이터베이스에 사용자 생성
        response = supabase.table("users").insert(user_insert_data).execute()
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 생성에 실패했습니다"
            )
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 생성 중 오류가 발생했습니다"
        )