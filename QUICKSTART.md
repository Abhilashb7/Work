# ⚡ 2-Minute Quick Start Guide

**Get your 100 job applications automated in 2 minutes!**

## 🚀 Ultra-Fast Setup

### Step 1: Install Everything (30 seconds)
```bash
./install.sh
```
*This installs Python dependencies and sets up everything automatically.*

### Step 2: Configure Your Details (60 seconds)
Edit `config.json` with your information:

```json
{
  "user_info": {
    "first_name": "John",
    "last_name": "Doe", 
    "email": "john@example.com",
    "phone": "+1-555-123-4567"
  },
  "login_credentials": {
    "email": "john@example.com",     ← YOUR LOGIN EMAIL
    "password": "your_password"      ← YOUR PASSWORD
  },
  "attachments": {
    "resume": "files/resume.pdf"     ← YOUR RESUME PATH
  }
}
```

### Step 3: Add Your Resume (10 seconds)
```bash
cp /path/to/your/resume.pdf files/resume.pdf
```

### Step 4: Launch Automation (10 seconds)
```bash
source venv/bin/activate
python launcher.py
# Choose option 1 for 10-tab processing
```

## 🎯 That's It!

Your automation will now:
- ✅ Open 10 browser tabs simultaneously
- ✅ Auto-login to each job portal
- ✅ Fill ALL forms instantly (zero delays)
- ✅ Navigate through multi-step applications
- ✅ Stop at submit for your review

## 📊 Monitor Progress

Open the real-time dashboard:
```bash
python launcher.py
# Choose option 5
```

## ⚡ Speed Modes

**Conservative (5 tabs)**: `python main.py jobs.csv 5`
**Standard (10 tabs)**: `python main.py jobs.csv 10`
**Ultra Fast (20 tabs)**: `python main.py jobs.csv 20`

## 🔧 Pre-Configured Jobs

The system comes with 30+ job URLs ready to test:
- Google, Microsoft, Amazon, Apple, Meta
- Netflix, Tesla, Spotify, Airbnb, Uber
- And many more top companies!

## 🎉 Success!

You should see output like:
```
🔥 PROCESSING BATCH 1: Jobs 1-10
⚡ [Google] INSTANT form filling...
✅ [Google] FULLY AUTOMATED processing completed!
⚡ [Microsoft] INSTANT form filling...
✅ [Microsoft] FULLY AUTOMATED processing completed!
```

**Ready for manual review and submission!** 🚀

---

**Need help?** Run `python launcher.py` and choose option 9 for system status.