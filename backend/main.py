from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime, timedelta

from .database import get_db, create_tables
from .models import User, Profile, Application, JobBoardCredential, TaskStatus
from .schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    ProfileCreate, ProfileUpdate, ProfileResponse,
    ApplicationCreate, ApplicationResponse,
    JobBoardCredentialCreate, JobBoardCredentialResponse,
    DashboardResponse, AdminApplicationCreate, AdminTaskAction
)
from .auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
)
from .celery_config import celery_app

# Create FastAPI app
app = FastAPI(
    title="B2C Job Application Platform API",
    description="Backend API for the B2C job application automation platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs("uploads/resumes", exist_ok=True)
os.makedirs("uploads/cover_letters", exist_ok=True)
os.makedirs("uploads/screenshots", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# ===============================
# AUTHENTICATION ENDPOINTS
# ===============================

@app.post("/auth/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/auth/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ===============================
# PROFILE ENDPOINTS
# ===============================

@app.post("/api/v1/profile", response_model=ProfileResponse)
def create_profile(
    profile: ProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if profile already exists
    existing_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    db_profile = Profile(**profile.dict(), user_id=current_user.id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.get("/api/v1/profile", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put("/api/v1/profile", response_model=ProfileResponse)
def update_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    return profile

@app.post("/api/v1/profile/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get user profile
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Save file
    file_path = f"uploads/resumes/{current_user.id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update profile
    profile.resume_filename = file.filename
    db.commit()
    
    return {"message": "Resume uploaded successfully", "filename": file.filename}

@app.post("/api/v1/profile/upload-cover-letter")
async def upload_cover_letter(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get user profile
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Save file
    file_path = f"uploads/cover_letters/{current_user.id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update profile
    profile.cover_letter_filename = file.filename
    db.commit()
    
    return {"message": "Cover letter uploaded successfully", "filename": file.filename}

# ===============================
# APPLICATION ENDPOINTS
# ===============================

@app.get("/api/v1/applications", response_model=List[ApplicationResponse])
def get_applications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    applications = db.query(Application).filter(Application.user_id == current_user.id).all()
    return applications

@app.get("/api/v1/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get profile
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    # Get all applications
    applications = db.query(Application).filter(Application.user_id == current_user.id).all()
    
    # Get recent activity (last 10)
    recent_activity = db.query(Application).filter(
        Application.user_id == current_user.id
    ).order_by(Application.updated_at.desc()).limit(10).all()
    
    return DashboardResponse(
        user=current_user,
        profile=profile,
        applications=applications,
        recent_activity=recent_activity
    )

# ===============================
# JOB BOARD CREDENTIALS ENDPOINTS
# ===============================

@app.post("/api/v1/credentials", response_model=JobBoardCredentialResponse)
def create_job_board_credential(
    credential: JobBoardCredentialCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Encrypt password (you should use proper encryption)
    encrypted_password = get_password_hash(credential.password)
    
    db_credential = JobBoardCredential(
        user_id=current_user.id,
        domain=credential.domain,
        email=credential.email,
        encrypted_password=encrypted_password
    )
    db.add(db_credential)
    db.commit()
    db.refresh(db_credential)
    return db_credential

@app.get("/api/v1/credentials", response_model=List[JobBoardCredentialResponse])
def get_job_board_credentials(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    credentials = db.query(JobBoardCredential).filter(
        JobBoardCredential.user_id == current_user.id
    ).all()
    return credentials

# ===============================
# ADMIN ENDPOINTS
# ===============================

@app.post("/admin/api/v1/apply")
def admin_create_application(
    application: AdminApplicationCreate,
    db: Session = Depends(get_db)
):
    # Verify user exists
    user = db.query(User).filter(User.id == application.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create application record
    db_application = Application(
        user_id=application.user_id,
        company=application.company,
        job_title=application.job_title,
        job_url=application.job_url,
        status="Pending"
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    # Queue the job application task
    from worker.tasks import apply_to_job
    task = apply_to_job.delay(db_application.id)
    
    # Update application with task ID
    db_application.task_id = task.id
    db.commit()
    
    return {"message": "Application queued successfully", "application_id": db_application.id, "task_id": task.id}

@app.post("/admin/api/v1/tasks/{task_id}/action")
def admin_task_action(
    task_id: str,
    action: AdminTaskAction,
    db: Session = Depends(get_db)
):
    # Find the application by task ID
    application = db.query(Application).filter(Application.task_id == task_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if action.action == "resume":
        # Resume the task
        from worker.tasks import resume_application_task
        resume_application_task.delay(application.id)
        application.status = "In Progress"
    elif action.action == "complete":
        # Mark as completed
        application.status = "Applied"
        application.date_applied = datetime.utcnow()
        if action.notes:
            application.notes = action.notes
    elif action.action == "fail":
        # Mark as failed
        application.status = "Failed"
        if action.notes:
            application.error_message = action.notes
    
    db.commit()
    return {"message": f"Task {action.action} successfully"}

@app.get("/admin/api/v1/applications")
def admin_get_all_applications(db: Session = Depends(get_db)):
    applications = db.query(Application).all()
    return applications

@app.get("/admin/api/v1/tasks/pending")
def admin_get_pending_tasks(db: Session = Depends(get_db)):
    pending_applications = db.query(Application).filter(
        Application.status.in_(["Pending", "In Progress"])
    ).all()
    return pending_applications

# ===============================
# FRONTEND SERVING
# ===============================

@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    return FileResponse("frontend/index.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    return FileResponse("frontend/dashboard.html")

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin():
    return FileResponse("frontend/admin.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)