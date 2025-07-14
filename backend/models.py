from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")
    job_board_credentials = relationship("JobBoardCredential", back_populates="user")

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Personal Information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    linkedin = Column(String)
    portfolio = Column(String)
    
    # Professional Information
    salary_expectation = Column(String)
    cover_letter = Column(Text)
    resume_filename = Column(String)
    cover_letter_filename = Column(String)
    
    # Q&A Configuration (stored as JSON)
    questions_config = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Job Information
    company = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    job_url = Column(String, nullable=False)
    
    # Application Status
    status = Column(String, default="Pending")  # Pending, In Progress, Applied, Failed, Interviewing
    task_id = Column(String, unique=True)  # Celery task ID
    
    # Metadata
    date_applied = Column(DateTime(timezone=True))
    error_message = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="applications")

class JobBoardCredential(Base):
    __tablename__ = "job_board_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Job Board Information
    domain = Column(String, nullable=False)  # e.g., "myworkdayjobs.com"
    email = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="job_board_credentials")

class TaskStatus(Base):
    __tablename__ = "task_status"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    
    status = Column(String, nullable=False)  # PENDING, IN_PROGRESS, WAITING_FOR_CREDENTIALS, WAITING_FOR_REVIEW, COMPLETED, FAILED
    message = Column(Text)
    screenshot_path = Column(String)  # For review purposes
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())