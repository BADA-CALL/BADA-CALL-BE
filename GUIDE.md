# 🌊 BADA-CALL-AI 사용 가이드

BADA-CALL-AI 프로젝트를 사용하는 완전한 가이드입니다. 초기 설정부터 실제 운영까지 모든 과정을 단계별로 설명합니다.

## 📋 목차

1. [초기 설정](#초기-설정)
2. [독립 서버 사용법](#독립-서버-사용법)
3. [FastAPI 통합 사용법](#fastapi-통합-사용법)
4. [API 명세서](#api-명세서)
5. [테스트 방법](#테스트-방법)
6. [문제 해결](#문제-해결)

---

## 🔧 초기 설정

### 1. 프로젝트 클론 및 의존성 설치

```bash
# 프로젝트 클론
git clone https://github.com/BADA-CALL/BADA-CALL-AI.git
cd BADA-CALL-AI

# 파이썬 가상환경 생성 (권장)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (Ngrok 토큰 설정)
# NGROK_AUTH_TOKEN=your_ngrok_token_here
```

**Ngrok 토큰 발급**: https://dashboard.ngrok.com/get-started/your-authtoken

### 3. 데이터 파일 확인

프로젝트 루트에 다음 파일들이 있는지 확인:
- `accident.csv` - 해양사고 통계 데이터
- `weather.csv` - 기상청 부이 데이터

---

## 🏃‍♂️ 독립 서버 사용법

### Smart Detection 서버 (스마트폰 센서 기반 사고 감지)

#### 1. 모델 학습 (최초 1회)

```bash
cd smart_detection
python train_har_model.py
```

**출력 예시**:
```
✅ har_model.tflite 생성 완료.
```

#### 2. Flask 서버 실행

```bash
python app_server.py
```

**출력 예시**:
```
🚀 BADA-CALL-AI 서버 초기화 중...
🌐 Ngrok 터널 개설 중...
🌍 외부 접속 주소 생성 성공!
🔗 Sensor Logger 앱 URL: https://abc123.ngrok.io/predict
```

#### 3. 스마트폰 앱 설정

1. **Sensor Logger** 앱 설치 (Android/iOS)
2. 앱에서 서버 URL 설정: `https://abc123.ngrok.io/predict`
3. 센서 데이터 전송 시작

### Risk Prediction 모듈 (위험도 예측)

```bash
cd risk_prediction
python test_risk.py
```

**출력 예시**:
```
상황              | 풍속  | 파고  | 확률   | 등급
-------------------------------------------------------
매우 안전         |   2.0 |   0.3 |   8.2% | 🟢 안전
주의보 수준       |  12.0 |   2.5 |  45.7% | 🟡 주의
위험(폭풍우)      |  18.0 |   5.0 |  78.3% | 🔴 위험
```

---

## 🚀 FastAPI 통합 사용법 (권장)

### 1. FastAPI 의존성 설치

```bash
# FastAPI 전용 의존성 설치
pip install -r fastapi_requirements.txt
```

### 2. FastAPI 서버 실행

```bash
python fastapi_integration_example.py
```

**출력 예시**:
```
🚀 BADA-CALL-AI FastAPI 서버 시작...
📖 API 문서: http://localhost:8000/docs
🔍 헬스체크: http://localhost:8000/health
🧠 BADA 위험도 예측 모델 로딩 중...
✅ BADA 모델 로드 완료!
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 3. API 문서 확인

브라우저에서 `http://localhost:8000/docs` 접속하여 자동 생성된 API 문서 확인

### 4. 다른 서비스에서 호출 예시

```python
import requests

# 사고 감지 요청
response = requests.post("http://localhost:8000/bada/accident-detection", json={
    "payload": [{
        "name": "accelerometer",
        "values": {"x": 20.0, "y": 15.0, "z": 18.5}
    }]
})
result = response.json()
print(f"사고 감지: {result['message']}")

# 위험도 예측 요청
response = requests.post("http://localhost:8000/bada/risk-prediction", json={
    "wind_speed": 18.0,
    "max_wave_height": 4.0,
    "significant_wave_height": 3.0
})
result = response.json()
print(f"위험도: {result['risk_percentage']}% ({result['risk_level']})")
```

---

## 📡 API 명세서

### 1. 사고 감지 API

**Endpoint**: `POST /bada/accident-detection`

**Request**:
```json
{
  "payload": [
    {
      "name": "accelerometer",
      "values": {
        "x": 0.0,
        "y": 9.8,
        "z": 0.0
      }
    }
  ]
}
```

**Response**:
```json
{
  "is_accident": 0,
  "confidence": 0.0,
  "message": "✅ 정상",
  "max_acceleration": 9.8
}
```

**판정 기준**:
- 최대 가속도 > 15.0 m/s² → 사고로 판정

### 2. 위험도 예측 API

**Endpoint**: `POST /bada/risk-prediction`

**Request**:
```json
{
  "wind_speed": 12.0,
  "max_wave_height": 2.5,
  "significant_wave_height": 1.8
}
```

**Response**:
```json
{
  "risk_percentage": 45.7,
  "risk_level": "🟡 주의",
  "wind_speed": 12.0,
  "max_wave_height": 2.5,
  "significant_wave_height": 1.8
}
```

**위험도 등급**:
- 🟢 안전 (5~20%): 기상 위험 낮음
- 🟡 주의 (20~60%): 기상 악화 시작, 주의 요망
- 🔴 위험 (60~85%): 사고 확률 높음, 출항 자제

### 3. 종합 분석 API

**Endpoint**: `POST /bada/comprehensive-analysis`

**Request**:
```json
{
  "sensor_data": {
    "payload": [
      {
        "name": "accelerometer",
        "values": {"x": 12.0, "y": 10.5, "z": 8.2}
      }
    ]
  },
  "weather_data": {
    "wind_speed": 15.0,
    "max_wave_height": 2.5,
    "significant_wave_height": 2.0
  }
}
```

**Response**:
```json
{
  "accident_detection": {
    "is_accident": 0,
    "confidence": 0.0,
    "message": "✅ 정상",
    "max_acceleration": 12.0
  },
  "risk_prediction": {
    "risk_percentage": 52.3,
    "risk_level": "🟡 주의"
  },
  "overall_status": "🟡 주의 상황 - 기상 모니터링 필요"
}
```

### 4. 헬스체크 API

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "risk_model_loaded": true,
  "message": "BADA-CALL-AI 서비스가 정상 작동 중입니다"
}
```

---

## 🧪 테스트 방법

### 1. 통합 테스트 실행

```bash
# FastAPI 서버가 실행 중인 상태에서
python client_example.py
```

**예상 출력**:
```
🚀 BADA FastAPI 클라이언트 테스트 시작

💚 헬스체크 테스트...
헬스체크: {'status': 'healthy', 'risk_model_loaded': True}

🔍 사고 감지 API 테스트...
정상 상황: {'is_accident': 0, 'message': '✅ 정상'}
사고 상황: {'is_accident': 1, 'message': '🚨 사고 감지!'}

🌊 위험도 예측 API 테스트...
안전 기상: {'risk_percentage': 8.2, 'risk_level': '🟢 안전'}
위험 기상: {'risk_percentage': 78.3, 'risk_level': '🔴 위험'}

✅ 모든 테스트 완료!
```

### 2. cURL 테스트

```bash
# 사고 감지 테스트
curl -X POST http://localhost:8000/bada/accident-detection \
  -H "Content-Type: application/json" \
  -d '{"payload": [{"name": "accelerometer", "values": {"x": 20.0, "y": 15.0, "z": 18.5}}]}'

# 위험도 예측 테스트
curl -X POST http://localhost:8000/bada/risk-prediction \
  -H "Content-Type: application/json" \
  -d '{"wind_speed": 18.0, "max_wave_height": 4.0, "significant_wave_height": 3.0}'
```

### 3. 수동 테스트

1. **브라우저에서 API 문서 접근**: `http://localhost:8000/docs`
2. **Try it out** 버튼으로 직접 API 호출
3. **Request body** 영역에 JSON 데이터 입력
4. **Execute** 버튼으로 실행 및 결과 확인

---

## ❗ 문제 해결

### 1. 모듈 임포트 오류

**오류**: `ModuleNotFoundError: No module named 'risk_prediction'`

**해결책**:
```bash
# 프로젝트 루트 디렉토리에서 실행하는지 확인
cd /path/to/BADA-CALL-AI
python fastapi_integration_example.py
```

### 2. 모델 로드 실패

**오류**: `❌ 모델 로드 실패: [Errno 2] No such file or directory: 'accident.csv'`

**해결책**:
```bash
# CSV 파일이 프로젝트 루트에 있는지 확인
ls -la *.csv
# accident.csv와 weather.csv 파일이 있어야 함
```

### 3. Ngrok 인증 오류

**오류**: `⚠️ 경고: NGROK_AUTH_TOKEN 환경변수가 설정되지 않았습니다.`

**해결책**:
```bash
# .env 파일에 Ngrok 토큰 추가
echo "NGROK_AUTH_TOKEN=your_token_here" >> .env
```

### 4. 포트 충돌

**오류**: `Address already in use`

**해결책**:
```bash
# 사용 중인 프로세스 종료
lsof -ti:8000 | xargs kill -9

# 또는 다른 포트 사용
uvicorn main:app --port 8001
```

### 5. 의존성 충돌

**오류**: `ImportError: cannot import name ...`

**해결책**:
```bash
# 가상환경 재생성
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r fastapi_requirements.txt
```

---

## 🎯 운영 환경 배포

### Docker 사용 (권장)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r fastapi_requirements.txt

EXPOSE 8000
CMD ["python", "fastapi_integration_example.py"]
```

### 서비스 모니터링

```bash
# 헬스체크로 서비스 상태 확인
curl http://localhost:8000/health

# 로그 모니터링
tail -f app.log
```

---

## 📞 지원

- **이슈 보고**: GitHub Issues
- **문서**: README.md, CLAUDE.md
- **예시 코드**: client_example.py

---

**🌊 BADA-CALL-AI로 더 안전한 바다를 만들어가세요!**