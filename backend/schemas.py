from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Profile Schemas
class ProfileCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    salary_expectation: Optional[str] = None
    cover_letter: Optional[str] = None
    questions_config: Optional[Dict[str, Any]] = None

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    salary_expectation: Optional[str] = None
    cover_letter: Optional[str] = None
    questions_config: Optional[Dict[str, Any]] = None

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    linkedin: Optional[str]
    portfolio: Optional[str]
    salary_expectation: Optional[str]
    cover_letter: Optional[str]
    resume_filename: Optional[str]
    cover_letter_filename: Optional[str]
    questions_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Application Schemas
class ApplicationCreate(BaseModel):
    company: str
    job_title: str
    job_url: str

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    company: str
    job_title: str
    job_url: str
    status: str
    task_id: Optional[str]
    date_applied: Optional[datetime]
    error_message: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Job Board Credential Schemas
class JobBoardCredentialCreate(BaseModel):
    domain: str
    email: str
    password: str

class JobBoardCredentialResponse(BaseModel):
    id: int
    user_id: int
    domain: str
    email: str
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Task Status Schemas
class TaskStatusResponse(BaseModel):
    id: int
    task_id: str
    application_id: int
    status: str
    message: Optional[str]
    screenshot_path: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Dashboard Response
class DashboardResponse(BaseModel):
    user: UserResponse
    profile: Optional[ProfileResponse]
    applications: List[ApplicationResponse]
    recent_activity: List[ApplicationResponse]

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Admin Schemas
class AdminTaskAction(BaseModel):
    action: str  # "resume", "complete", "fail"
    notes: Optional[str] = None

class AdminApplicationCreate(BaseModel):
    user_id: int
    company: str
    job_title: str
    job_url: str