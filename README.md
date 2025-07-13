# Enhanced Job Application Automation Tool

An advanced, lightning-fast job application automation tool that automatically fills forms on job boards using Playwright. This enhanced version handles both traditional HTML forms and modern custom dropdown components.

## Key Features

✅ **Enhanced Dropdown Support**: Handles both native HTML selects and modern custom dropdowns  
✅ **Smart Field Detection**: Uses multiple strategies to find and fill form fields  
✅ **Multi-Strategy Approach**: Tries various selectors and methods for maximum compatibility  
✅ **File Upload Automation**: Automatically uploads resumes and cover letters  
✅ **Customizable Questions**: Pre-configured answers for common application questions  
✅ **Error Recovery**: Robust error handling with fallback strategies  
✅ **Fast Execution**: Optimized for speed while maintaining reliability  

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install
```

### 3. Configure Your Information

Edit `config.json` with your personal information:

```json
{
  "user_info": {
    "first_name": "Your First Name",
    "last_name": "Your Last Name",
    "email": "your.email@example.com",
    "phone": "+1-555-123-4567",
    // ... add all your details
  },
  "attachments": {
    "resume": "files/your_resume.pdf",
    "cover_letter": "files/your_cover_letter.pdf"
  },
  "questions": [
    {
      "keywords": ["experience", "years", "work"],
      "answer": "5+ years"
    }
    // ... customize for your situation
  ]
}
```

### 4. Add Your Documents

Place your documents in the `files/` directory:
- `files/your_resume.pdf`
- `files/your_cover_letter.pdf`

### 5. Create Job List

Edit `jobs.csv` with the job URLs you want to apply to:

```csv
company,url
Google,https://careers.google.com/jobs/results/actual-job-id/
Microsoft,https://careers.microsoft.com/actual-job-url
```

## Usage

### Basic Usage

```bash
python main.py jobs.csv
```

### Features Explained

#### 1. Enhanced Dropdown Handling

The tool now handles:
- **Native HTML selects**: Traditional `<select>` dropdowns
- **Custom dropdowns**: Modern div-based dropdowns with role="combobox"
- **Button dropdowns**: Dropdowns triggered by buttons
- **Searchable dropdowns**: Dropdowns with search functionality

#### 2. Smart Field Detection

Uses multiple selector strategies:
- Name attributes
- ID attributes  
- Placeholder text
- ARIA labels
- Data attributes
- Adjacent labels

#### 3. Multi-Strategy Question Handling

For each question, tries:
1. Native dropdown selection
2. Custom dropdown interaction
3. Radio button selection
4. Checkbox handling
5. Text input filling

#### 4. Robust File Upload

Handles various upload patterns:
- Direct file input elements
- Button-triggered file choosers
- Drag-and-drop areas
- Custom upload components

## Configuration Guide

### User Information Fields

```json
"user_info": {
  "first_name": "John",           // First name
  "last_name": "Doe",             // Last name  
  "email": "john@example.com",    // Email address
  "phone": "+1-555-123-4567",     // Phone number
  "address": "123 Main Street",   // Street address
  "city": "San Francisco",        // City
  "state": "California",          // State/Province
  "zip_code": "94105",           // ZIP/Postal code
  "linkedin": "https://...",      // LinkedIn URL
  "portfolio": "https://...",     // Portfolio website
  "salary": "120000"             // Expected salary
}
```

### Question Configuration

```json
"questions": [
  {
    "keywords": ["experience", "years", "work experience"],
    "answer": "5+ years"
  },
  {
    "keywords": ["authorized", "visa", "work authorization"],
    "answer": "Yes"
  }
]
```

**Tips for Questions:**
- Use multiple keywords for better matching
- Include variations and synonyms
- Test your answers on actual forms

### Automation Settings

```json
"automation_settings": {
  "headless": false,        // Set to true for background operation
  "slow_mo": 100,          // Delay between actions (milliseconds)
  "timeout": 30000,        // Element timeout (milliseconds)
  "wait_between_actions": 1000,  // Additional wait time
  "max_retries": 3         // Retry attempts for failed operations
}
```

## Advanced Usage

### Speed Optimization

For maximum speed:
```json
"automation_settings": {
  "headless": true,
  "slow_mo": 50,
  "timeout": 15000
}
```

### Debug Mode

For troubleshooting:
```json
"automation_settings": {
  "headless": false,
  "slow_mo": 500,
  "timeout": 60000
}
```

## Troubleshooting

### Common Issues

1. **Dropdown not working**
   - Check if the site uses custom dropdowns
   - Add more specific keywords to your question
   - Verify the answer text matches exactly

2. **Fields not filling**
   - Check field names in browser developer tools
   - Add alternative keywords for the field
   - Verify your config.json syntax

3. **File upload failing**
   - Ensure file paths are correct
   - Check file permissions
   - Verify file formats are supported

### Debugging Tips

1. **Run with browser visible**: Set `"headless": false`
2. **Slow down actions**: Increase `"slow_mo"` value
3. **Check logs**: Monitor console output for errors
4. **Inspect elements**: Use browser dev tools to find selectors

## Legal Disclaimer

This tool is for educational and legitimate job application purposes only. Users are responsible for:
- Complying with website terms of service
- Ensuring accuracy of submitted information
- Following applicable laws and regulations
- Respecting rate limits and server resources

## Support

For issues or improvements:
1. Check the troubleshooting section
2. Review your configuration files
3. Test with a single job application first
4. Verify website compatibility

## Version History

- **v2.0**: Enhanced dropdown support, multi-strategy handling
- **v1.0**: Basic form filling functionality

---

**Happy job hunting! 🚀**