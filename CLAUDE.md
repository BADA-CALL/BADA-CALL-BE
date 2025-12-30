# 바다콜 Backend

바다 한가운데에서 사고 발생 시 GPS 기반 자동 사고 감지 및 긴급 신고 API

---

## 구현 단계별 투두 리스트

### 1. 프로젝트 초기 설정
- [ ] 프로젝트 초기 설정 및 구조 생성
- [ ] 기본 의존성 설치 및 환경 설정 (requirements.txt, .env)

### 2. 백엔드 기본 구조
- [ ] FastAPI 기본 앱 구조 생성 (main.py, config.py)
- [ ] Supabase 연결 및 데이터베이스 설정 (database.py)

### 3. 데이터 모델링
- [ ] Pydantic 모델 정의 (User, Report - models.py)

### 4. 인증 시스템
- [ ] JWT 인증 시스템 구현 (auth.py)

### 5. API 엔드포인트
- [ ] 사용자 관련 API 엔드포인트 구현 (users.py)
- [ ] 신고 관련 API 엔드포인트 구현 (reports.py)

### 6. 핵심 로직
- [ ] 센서 데이터 처리 로직 구현
- [ ] 자동 사고 감지 알고리즘 구현

### 7. 네트워크 안정성
- [ ] 오프라인 큐잉 및 재전송 로직 구현

### 8. 테스트 및 마무리
- [ ] API 테스트 및 문서화

---

## 기술 스택

- **FastAPI** - 웹 프레임워크
- **Supabase** - PostgreSQL + Storage
- **PyJWT** - JWT 인증
- **Uvicorn** - ASGI 서버

---

## 파일 구조
```
app/
├── main.py          # FastAPI 앱 진입점
├── config.py        # 환경변수 설정
├── models.py        # Pydantic 모델
├── database.py      # Supabase 클라이언트
└── routers/
    ├── auth.py      # 인증 API
    ├── users.py     # 사용자 API
    └── reports.py   # 신고 API
```

---

## 실행
```bash
# 설치
pip install -r requirements.txt

# .env 설정
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SECRET_KEY=your-secret-key

# 실행
uvicorn app.main:app --reload

# API 문서
http://localhost:8000/docs
```

---

## 데이터베이스

**users**: id, name, phone, boat_info, emergency_contacts
**reports**: id, user_id, type, location, sensor_data, status, timestamp

---

## 네트워크 전략

바다 한가운데는 LTE 불가 → 오프라인 큐잉 + 재전송 로직 필요

**프론트**: 로컬 저장 → 연결 복구 시 전송
**백엔드**: 재전송 요청 처리 + 중복 방지