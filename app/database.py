from supabase import create_client, Client
from app.config import settings

# Supabase client - 실제 사용 시 올바른 URL과 Key를 .env에 설정하세요
try:
    supabase: Client = create_client(settings.supabase_url, settings.supabase_anon_key)
    print("✅ Supabase 연결 성공")
except Exception as e:
    print(f"⚠️  Supabase 연결 실패: {e}")
    print("📝 .env 파일에 올바른 SUPABASE_URL과 SUPABASE_ANON_KEY를 설정해주세요")
    supabase = None