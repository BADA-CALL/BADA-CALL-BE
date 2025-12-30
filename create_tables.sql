-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    boat_name TEXT,
    boat_number TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 신고 테이블
CREATE TABLE IF NOT EXISTS reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('manual', 'auto_detection')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'dispatched', 'completed', 'cancelled')),
    location_latitude FLOAT NOT NULL,
    location_longitude FLOAT NOT NULL,
    location_address TEXT,
    sensor_data JSONB,
    accident_probability FLOAT DEFAULT 0,
    voice_file_url TEXT,
    video_file_url TEXT,
    description TEXT,
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 위치 데이터 테이블 (GPS 추적용)
CREATE TABLE IF NOT EXISTS locations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    accuracy FLOAT,
    altitude FLOAT,
    speed FLOAT,
    heading FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS (Row Level Security) 설정
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;

-- 사용자 정책
DROP POLICY IF EXISTS "Users can view all users" ON users;
DROP POLICY IF EXISTS "Users can insert" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;

CREATE POLICY "Users can view all users" ON users FOR SELECT USING (true);
CREATE POLICY "Users can insert" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (true);

-- 신고 정책
DROP POLICY IF EXISTS "Users can view own reports" ON reports;
DROP POLICY IF EXISTS "Users can insert own reports" ON reports;
DROP POLICY IF EXISTS "Users can update own reports" ON reports;

CREATE POLICY "Users can view own reports" ON reports FOR SELECT USING (true);
CREATE POLICY "Users can insert own reports" ON reports FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update own reports" ON reports FOR UPDATE USING (true);

-- 위치 정책
DROP POLICY IF EXISTS "Users can view own locations" ON locations;
DROP POLICY IF EXISTS "Users can insert own locations" ON locations;

CREATE POLICY "Users can view own locations" ON locations FOR SELECT USING (true);
CREATE POLICY "Users can insert own locations" ON locations FOR INSERT WITH CHECK (true);