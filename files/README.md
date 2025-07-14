# 📁 Files Directory

**Place your documents here for automatic upload during job applications.**

## Required Files

### Resume (Required)
- **File**: `resume.pdf`
- **Format**: PDF recommended
- **Purpose**: Automatically uploaded during applications

### Cover Letter (Optional)
- **File**: `cover_letter.pdf` 
- **Format**: PDF recommended
- **Purpose**: Uploaded when cover letter fields are detected

## Example Structure
```
files/
├── resume.pdf           ← Your main resume
├── cover_letter.pdf     ← Optional cover letter
└── portfolio.pdf        ← Optional portfolio/work samples
```

## Tips
- ✅ Use **PDF format** for best compatibility
- ✅ Keep file names **simple** (no spaces or special characters)
- ✅ Make sure files are **under 10MB** each
- ✅ Update your **config.json** to match file paths

## Configuration

Update `config.json` to reference your files:

```json
{
  "attachments": {
    "resume": "files/resume.pdf",
    "cover_letter": "files/cover_letter.pdf"
  }
}
```

---

**Ready to upload your documents and start automating!** 🚀