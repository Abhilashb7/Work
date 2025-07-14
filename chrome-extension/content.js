// Content script for Job Application Assistant Chrome Extension
(function() {
    'use strict';
    
    // Default configuration
    const DEFAULT_CONFIG = {
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
    };
    
    let config = DEFAULT_CONFIG;
    let isProcessing = false;
    
    // Load configuration from storage
    loadConfig();
    
    // Listen for messages from popup
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        switch (message.action) {
            case 'checkStatus':
                sendResponse({
                    loginDetected: isLoginPage(),
                    isJobPage: isJobApplicationPage()
                });
                break;
                
            case 'fillForm':
                if (!isProcessing) {
                    fillForm(message.settings).then(result => {
                        sendResponse(result);
                    }).catch(error => {
                        sendResponse({success: false, error: error.message});
                    });
                    return true; // Keep message channel open for async response
                }
                break;
                
            case 'checkPostLogin':
                sendResponse({
                    loginComplete: !isLoginPage()
                });
                break;
        }
    });
    
    async function loadConfig() {
        try {
            const stored = await chrome.storage.sync.get('userConfig');
            if (stored.userConfig) {
                config = {...DEFAULT_CONFIG, ...stored.userConfig};
            }
        } catch (error) {
            console.log('Using default config:', error);
        }
    }
    
    function isLoginPage() {
        // Check for login indicators
        const loginIndicators = [
            'input[type="password"]',
            'input[name*="password" i]',
            'input[id*="password" i]',
            'button:contains("Sign In")',
            'button:contains("Log In")',
            'button:contains("Login")',
            '.login-form',
            '.signin-form',
            '#login-form'
        ];
        
        for (const indicator of loginIndicators) {
            if (document.querySelector(indicator)) {
                return true;
            }
        }
        
        // Check URL and title
        const url = window.location.href.toLowerCase();
        const title = document.title.toLowerCase();
        const loginPatterns = ['login', 'signin', 'auth', 'sso', 'portal'];
        
        return loginPatterns.some(pattern => url.includes(pattern) || title.includes(pattern));
    }
    
    function isJobApplicationPage() {
        // Check for job application indicators
        const jobPageIndicators = [
            'input[placeholder*="first name" i]',
            'input[placeholder*="last name" i]',
            'input[placeholder*="email" i]',
            'button:contains("Apply")',
            'button:contains("Submit Application")',
            '.application-form',
            '#application-form',
            'form[action*="apply" i]'
        ];
        
        return jobPageIndicators.some(selector => document.querySelector(selector));
    }
    
    async function fillForm(settings) {
        if (isProcessing) {
            return {success: false, error: 'Already processing'};
        }
        
        isProcessing = true;
        
        try {
            updateProgress(0);
            log('🚀 Starting form fill process');
            
            // Step 1: Fill text inputs (40%)
            await fillTextInputs();
            updateProgress(40);
            
            // Step 2: Handle questions and dropdowns (40%)
            await handleQuestions();
            updateProgress(80);
            
            // Step 3: Handle file uploads (20%)
            await handleFileUploads();
            updateProgress(100);
            
            log('✅ Form filling completed successfully!');
            return {success: true};
            
        } catch (error) {
            log('❌ Form filling failed: ' + error.message);
            return {success: false, error: error.message};
        } finally {
            isProcessing = false;
        }
    }
    
    async function fillTextInputs() {
        log('📝 Filling text inputs...');
        
        for (const [key, value] of Object.entries(config.user_info)) {
            if (!value) continue;
            
            const selectors = [
                `input[name*="${key}" i]`,
                `input[id*="${key}" i]`,
                `input[placeholder*="${key}" i]`,
                `input[aria-label*="${key}" i]`,
                `input[data-automation-id*="${key}" i]`,
                `textarea[name*="${key}" i]`,
                `textarea[placeholder*="${key}" i]`
            ];
            
            const element = findElement(selectors);
            if (element) {
                await fillElement(element, value);
                log(`✅ Filled ${key}: ${value}`);
            }
        }
    }
    
    async function handleQuestions() {
        log('❓ Handling questions and dropdowns...');
        
        for (const question of config.questions) {
            let handled = false;
            
            for (const keyword of question.keywords) {
                if (handled) break;
                
                // Try different strategies
                if (await handleDropdown(keyword, question.answer)) {
                    log(`✅ Selected dropdown '${keyword}': ${question.answer}`);
                    handled = true;
                } else if (await handleCustomDropdown(keyword, question.answer)) {
                    log(`✅ Selected custom dropdown '${keyword}': ${question.answer}`);
                    handled = true;
                } else if (await handleRadioButtons(keyword, question.answer)) {
                    log(`✅ Selected radio '${keyword}': ${question.answer}`);
                    handled = true;
                } else if (await handleCheckboxes(keyword, question.answer)) {
                    log(`✅ Checked '${keyword}': ${question.answer}`);
                    handled = true;
                } else if (await handleTextInput(keyword, question.answer)) {
                    log(`✅ Filled text '${keyword}': ${question.answer}`);
                    handled = true;
                }
            }
            
            if (!handled) {
                log(`⚠️ Could not handle question: ${question.keywords.join(', ')}`);
            }
        }
    }
    
    async function handleDropdown(keyword, answer) {
        const selectors = [
            `select[name*="${keyword}" i]`,
            `select[id*="${keyword}" i]`,
            `select[aria-label*="${keyword}" i]`,
            `select[data-automation-id*="${keyword}" i]`
        ];
        
        const select = findElement(selectors);
        if (!select) return false;
        
        // Try to select by text
        for (const option of select.options) {
            if (option.text.toLowerCase().includes(answer.toLowerCase())) {
                select.value = option.value;
                triggerEvent(select, 'change');
                return true;
            }
        }
        
        // Try to select by value
        for (const option of select.options) {
            if (option.value.toLowerCase().includes(answer.toLowerCase())) {
                select.value = option.value;
                triggerEvent(select, 'change');
                return true;
            }
        }
        
        return false;
    }
    
    async function handleCustomDropdown(keyword, answer) {
        const triggerSelectors = [
            `div[role="combobox"][aria-label*="${keyword}" i]`,
            `button[aria-label*="${keyword}" i]`,
            `div[data-automation-id*="${keyword}" i]`,
            `button[data-automation-id*="${keyword}" i]`
        ];
        
        const trigger = findElement(triggerSelectors);
        if (!trigger) return false;
        
        // Click to open dropdown
        trigger.click();
        await sleep(500);
        
        // Find and click option
        const optionSelectors = [
            `[role="option"]:contains("${answer}")`,
            `li:contains("${answer}")`,
            `div:contains("${answer}")`,
            `button:contains("${answer}")`
        ];
        
        const option = findElement(optionSelectors);
        if (option) {
            option.click();
            await sleep(200);
            return true;
        }
        
        return false;
    }
    
    async function handleRadioButtons(keyword, answer) {
        const selectors = [
            `input[type="radio"][value*="${answer}" i]`,
            `input[type="radio"][data-automation-id*="${answer}" i]`
        ];
        
        const radio = findElement(selectors);
        if (radio) {
            radio.checked = true;
            triggerEvent(radio, 'change');
            return true;
        }
        
        return false;
    }
    
    async function handleCheckboxes(keyword, answer) {
        if (!['yes', 'true', '1', 'agree', 'accept'].includes(answer.toLowerCase())) {
            return false;
        }
        
        const selectors = [
            `input[type="checkbox"][name*="${keyword}" i]`,
            `input[type="checkbox"][id*="${keyword}" i]`,
            `input[type="checkbox"][data-automation-id*="${keyword}" i]`
        ];
        
        const checkbox = findElement(selectors);
        if (checkbox) {
            checkbox.checked = true;
            triggerEvent(checkbox, 'change');
            return true;
        }
        
        return false;
    }
    
    async function handleTextInput(keyword, answer) {
        const selectors = [
            `input[placeholder*="${keyword}" i]`,
            `textarea[placeholder*="${keyword}" i]`,
            `input[aria-label*="${keyword}" i]`,
            `textarea[aria-label*="${keyword}" i]`
        ];
        
        const element = findElement(selectors);
        if (element) {
            await fillElement(element, answer);
            return true;
        }
        
        return false;
    }
    
    async function handleFileUploads() {
        log('📎 Handling file uploads...');
        
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        for (const input of fileInputs) {
            // Skip if already has files
            if (input.files.length > 0) continue;
            
            // Check if it's for resume/CV
            const context = getElementContext(input);
            if (context.includes('resume') || context.includes('cv')) {
                log('📄 Found resume upload field (manual upload required)');
                // Note: Chrome extensions can't automatically upload files for security
                // User needs to manually select files
            }
        }
    }
    
    function findElement(selectors) {
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) return element;
        }
        return null;
    }
    
    async function fillElement(element, value) {
        // Clear existing value
        element.value = '';
        element.focus();
        
        // Type character by character for better compatibility
        for (const char of value) {
            element.value += char;
            triggerEvent(element, 'input');
            await sleep(10);
        }
        
        triggerEvent(element, 'change');
        triggerEvent(element, 'blur');
    }
    
    function triggerEvent(element, eventType) {
        const event = new Event(eventType, {bubbles: true, cancelable: true});
        element.dispatchEvent(event);
    }
    
    function getElementContext(element) {
        // Get surrounding text context
        const parent = element.parentElement;
        const context = parent ? parent.textContent.toLowerCase() : '';
        
        // Also check labels
        const label = document.querySelector(`label[for="${element.id}"]`);
        if (label) {
            return context + ' ' + label.textContent.toLowerCase();
        }
        
        return context;
    }
    
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    function updateProgress(percent) {
        chrome.runtime.sendMessage({
            action: 'updateProgress',
            percent: percent
        });
    }
    
    function log(message, type = 'info') {
        console.log(`[JobApp] ${message}`);
        chrome.runtime.sendMessage({
            action: 'log',
            message: message,
            type: type
        });
    }
    
    // jQuery-like :contains selector
    function addContainsSelector() {
        if (!document.querySelector.originalFunction) {
            document.querySelector.originalFunction = document.querySelector;
            document.querySelectorAll.originalFunction = document.querySelectorAll;
            
            // Simple contains implementation
            const elementsContaining = (text) => {
                return Array.from(document.querySelectorAll('*')).filter(el => 
                    el.textContent.toLowerCase().includes(text.toLowerCase())
                );
            };
            
            window.elementsContaining = elementsContaining;
        }
    }
    
    // Initialize
    addContainsSelector();
    
    // Auto-detect login pages on load
    if (isLoginPage()) {
        chrome.runtime.sendMessage({
            action: 'statusUpdate',
            status: 'loginDetected'
        });
    }
    
    // Monitor for page changes (SPA support)
    let lastUrl = window.location.href;
    setInterval(() => {
        if (window.location.href !== lastUrl) {
            lastUrl = window.location.href;
            setTimeout(() => {
                if (isLoginPage()) {
                    chrome.runtime.sendMessage({
                        action: 'statusUpdate',
                        status: 'loginDetected'
                    });
                } else if (isJobApplicationPage()) {
                    chrome.runtime.sendMessage({
                        action: 'statusUpdate',
                        status: 'ready'
                    });
                }
            }, 1000);
        }
    }, 1000);
    
})();