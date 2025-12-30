from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class ReportType(str, Enum):
    MANUAL = "manual"
    AUTO_DETECTION = "auto_detection"

class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EmergencyType(str, Enum):
    COLLISION = "collision"
    ENGINE_FAILURE = "engine_failure"
    FIRE = "fire"
    MEDICAL_EMERGENCY = "medical_emergency"
    MAN_OVERBOARD = "man_overboard"
    SINKING = "sinking"
    OTHER = "other"

class Location(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    timestamp: Optional[datetime] = None

class SensorData(BaseModel):
    accelerometer: Optional[Dict[str, float]] = None
    gyroscope: Optional[Dict[str, float]] = None
    gps_speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: datetime

# Onboarding Models
class OnboardingData(BaseModel):
    device_id: str
    name: str
    phone: str
    boat_name: Optional[str] = None
    boat_number: Optional[str] = None
    emergency_contact_1_name: Optional[str] = None
    emergency_contact_1_phone: Optional[str] = None
    emergency_contact_2_name: Optional[str] = None
    emergency_contact_2_phone: Optional[str] = None

class OnboardingResponse(BaseModel):
    device_id: str
    message: str
    user_id: str

class EmergencyContact(BaseModel):
    name: str
    phone: str

class UserProfile(BaseModel):
    device_id: str
    name: str
    phone: str
    boat_name: Optional[str] = None
    boat_number: Optional[str] = None
    emergency_contacts: List[EmergencyContact] = []
    created_at: datetime

# Report Models
class EmergencyReportCreate(BaseModel):
    device_id: str
    type: ReportType = ReportType.MANUAL
    emergency_type: EmergencyType = EmergencyType.OTHER
    location_latitude: float
    location_longitude: float
    location_address: Optional[str] = None
    description: Optional[str] = None
    sensor_data: Optional[Dict] = None

class AutoDetectionReport(BaseModel):
    device_id: str
    type: ReportType = ReportType.AUTO_DETECTION
    location_latitude: float
    location_longitude: float
    sensor_data: Dict
    accident_probability: float

class ReportUpdate(BaseModel):
    status: Optional[ReportStatus] = None
    location_address: Optional[str] = None
    voice_file_url: Optional[str] = None
    video_file_url: Optional[str] = None
    description: Optional[str] = None

class ReportResponse(BaseModel):
    id: str
    device_id: str
    type: ReportType
    status: ReportStatus
    location_latitude: float
    location_longitude: float
    location_address: Optional[str]
    sensor_data: Optional[Dict]
    accident_probability: Optional[float]
    voice_file_url: Optional[str]
    video_file_url: Optional[str]
    description: Optional[str]
    reported_at: datetime
    updated_at: datetime

# Location Models
class LocationUpdate(BaseModel):
    device_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: Optional[datetime] = None

class LocationResponse(BaseModel):
    id: str
    device_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float]
    altitude: Optional[float]
    speed: Optional[float]
    heading: Optional[float]
    timestamp: datetime

# Legacy models (유지)
class ReportBase(BaseModel):
    type: ReportType
    location: Location
    sensor_data: Optional[SensorData] = None
    description: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: str
    user_id: str
    status: ReportStatus = ReportStatus.PENDING
    created_at: datetime
    updated_at: datetime