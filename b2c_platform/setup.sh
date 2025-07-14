#!/bin/bash

echo "🚀 Setting up JobFlow B2C Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. Installing..."
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib
    # macOS
    elif command -v brew &> /dev/null; then
        brew install postgresql
        brew services start postgresql
    else
        echo "❌ Please install PostgreSQL manually"
        exit 1
    fi
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "⚠️  Redis is not installed. Installing..."
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y redis-server
        sudo systemctl start redis-server
        sudo systemctl enable redis-server
    # macOS
    elif command -v brew &> /dev/null; then
        brew install redis
        brew services start redis
    else
        echo "❌ Please install Redis manually"
        exit 1
    fi
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create PostgreSQL database
echo "🗃️  Setting up PostgreSQL database..."
sudo -u postgres createdb b2c_platform_db 2>/dev/null || echo "Database might already exist"
sudo -u postgres psql -c "CREATE USER b2c_user WITH PASSWORD 'b2c_password';" 2>/dev/null || echo "User might already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE b2c_platform_db TO b2c_user;" 2>/dev/null

# Copy environment file
echo "⚙️  Setting up environment configuration..."
cp .env.example .env

# Update .env with actual database credentials
sed -i 's/postgresql:\/\/user:password@localhost:5432\/b2c_platform_db/postgresql:\/\/b2c_user:b2c_password@localhost:5432\/b2c_platform_db/' .env

# Generate a secure secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
sed -i "s/your-super-secret-key-here-change-this-in-production-make-it-long-and-random/$SECRET_KEY/" .env

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads/{resumes,cover_letters,screenshots}
mkdir -p logs

# Create startup scripts
echo "📝 Creating startup scripts..."

# Backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
source ../venv/bin/activate
python -c "from database import create_tables; create_tables()"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
EOF

# Worker startup script
cat > start_worker.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
cd worker
celery -A backend.celery_config:celery_app worker --loglevel=info --queues=job_applications,account_creation,review
EOF

# Make scripts executable
chmod +x start_backend.sh start_worker.sh

# Create a comprehensive README
cat > B2C_SETUP_README.md << 'EOF'
# 🚀 JobFlow B2C Platform Setup Complete!

## What's been set up:

### ✅ Backend API Server
- FastAPI application with all endpoints
- PostgreSQL database with proper schema
- JWT authentication system
- File upload handling

### ✅ AI Worker System  
- Celery task queue with Redis
- Automated job application processing
- Browser automation with Playwright
- Human-in-the-loop workflow

### ✅ Frontend Applications
- Client onboarding and dashboard
- Admin panel for task management
- Beautiful, responsive UI

### ✅ Database & Infrastructure
- PostgreSQL database: `b2c_platform_db`
- Redis for task queue
- File storage system

## 🚀 Quick Start:

### 1. Start the services:

Terminal 1 - Backend API:
```bash
./start_backend.sh
```

Terminal 2 - Worker Process:
```bash
./start_worker.sh
```

Terminal 3 - Redis (if not auto-started):
```bash
redis-server
```

### 2. Access the platform:

- **Client Portal**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/docs

### 3. Test the system:

1. Register a new client at http://localhost:8000
2. Complete the onboarding form with profile details
3. Upload resume and cover letter
4. Go to admin panel to create test applications
5. Monitor the automation process

## 🔧 Configuration:

Edit `.env` file to customize:
- Database settings
- Email notifications  
- Security settings
- Playwright options

## 📊 Monitoring:

- **Celery Flower** (optional): `pip install flower && celery flower`
- **Database**: Use pgAdmin or any PostgreSQL client
- **Logs**: Check console output and logs/ directory

## 🎯 Production Deployment:

1. Set `DEBUG=False` in .env
2. Configure proper domain in `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Set up SSL/TLS certificates
5. Configure production database
6. Set up monitoring and logging

## 🔐 Security Notes:

- Change all default passwords
- Use strong secret keys
- Enable HTTPS in production
- Implement rate limiting
- Regular security updates

## 🤝 Support:

This is a complete B2C job application automation platform based on your existing automation system. The AI handles 95% of the work while requiring human approval for critical steps.

Perfect for scaling your job application service to multiple clients!
EOF

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Review and edit .env file if needed"
echo "2. Start the backend: ./start_backend.sh"
echo "3. Start the worker: ./start_worker.sh"  
echo "4. Visit http://localhost:8000 to test the platform"
echo ""
echo "📖 Read B2C_SETUP_README.md for detailed instructions"
echo ""
echo "🚀 Your B2C Job Application Platform is ready!"