// Background service worker for Job Application Assistant Chrome Extension
chrome.runtime.onInstalled.addListener(() => {
    console.log('Job Application Assistant installed');
    
    // Set default configuration
    chrome.storage.sync.set({
        autoLogin: true,
        fastMode: true,
        showLogs: false,
        userConfig: {
            "user_info": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@email.com",
                "phone": "+1-555-123-4567",
                "address": "123 Main Street",
                "city": "San Francisco",
                "state": "California",
                "zip_code": "94105",
                "linkedin": "https://linkedin.com/in/johndoe",
                "portfolio": "https://johndoe.dev",
                "salary": "120000"
            },
            "questions": [
                {"keywords": ["experience", "years", "work", "years of experience"], "answer": "5+ years"},
                {"keywords": ["authorized", "visa", "work authorization", "eligible"], "answer": "Yes"},
                {"keywords": ["degree", "education", "qualification", "bachelor"], "answer": "Bachelor's Degree"},
                {"keywords": ["relocate", "relocation", "move", "willing to relocate"], "answer": "Yes"},
                {"keywords": ["salary", "compensation", "expected salary", "pay", "wage"], "answer": "120000"},
                {"keywords": ["start", "available", "notice", "when can you start"], "answer": "2 weeks"},
                {"keywords": ["remote", "work from home", "hybrid", "location"], "answer": "Yes"},
                {"keywords": ["travel", "willing to travel", "business travel"], "answer": "Yes"},
                {"keywords": ["sponsorship", "sponsor", "visa sponsorship"], "answer": "No"},
                {"keywords": ["citizen", "citizenship", "us citizen"], "answer": "Yes"}
            ]
        }
    });
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    switch (message.action) {
        case 'log':
            console.log(`[${sender.tab?.url}] ${message.message}`);
            break;
        case 'updateProgress':
            // Forward to popup if open
            chrome.runtime.sendMessage(message);
            break;
        case 'statusUpdate':
            // Forward to popup if open
            chrome.runtime.sendMessage(message);
            break;
    }
});

// Context menu for quick access
chrome.contextMenus.create({
    id: 'fillForm',
    title: '🚀 Fill Job Application Form',
    contexts: ['page'],
    documentUrlPatterns: ['*://*/*']
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'fillForm') {
        chrome.tabs.sendMessage(tab.id, {action: 'fillForm', settings: {fastMode: true}});
    }
});

// Badge management
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        // Check if it's a job site
        const jobSites = [
            'workday.com',
            'greenhouse.io',
            'lever.co',
            'indeed.com',
            'linkedin.com',
            'glassdoor.com',
            'monster.com',
            'careers.',
            'jobs.'
        ];
        
        const isJobSite = jobSites.some(site => tab.url.includes(site));
        
        if (isJobSite) {
            chrome.action.setBadgeText({text: '🎯', tabId: tabId});
            chrome.action.setBadgeBackgroundColor({color: '#28a745'});
        } else {
            chrome.action.setBadgeText({text: '', tabId: tabId});
        }
    }
});

// Keyboard shortcuts
chrome.commands.onCommand.addListener((command) => {
    if (command === 'fill-form') {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, {action: 'fillForm', settings: {fastMode: true}});
        });
    }
});