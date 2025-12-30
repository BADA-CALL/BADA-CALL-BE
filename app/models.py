from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class ReportType(str, Enum):
    COLLISION = "collision"
    ENGINE_FAILURE = "engine_failure"
    FIRE = "fire"
    MEDICAL_EMERGENCY = "medical_emergency"
    MAN_OVERBOARD = "man_overboard"
    OTHER = "other"

class ReportStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"

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

class EmergencyContact(BaseModel):
    name: str
    phone: str
    relationship: str

class UserBase(BaseModel):
    name: str
    phone: str
    boat_info: Optional[str] = None

class UserCreate(UserBase):
    emergency_contacts: Optional[List[EmergencyContact]] = []

class User(UserBase):
    id: str
    emergency_contacts: List[EmergencyContact] = []
    created_at: datetime

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