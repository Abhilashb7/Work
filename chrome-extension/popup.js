// Popup functionality for Job Application Assistant Chrome Extension
document.addEventListener('DOMContentLoaded', function() {
    const fillFormBtn = document.getElementById('fillForm');
    const loginHelpBtn = document.getElementById('loginHelp');
    const configBtn = document.getElementById('configBtn');
    const resetBtn = document.getElementById('resetBtn');
    const statusDiv = document.getElementById('status');
    const statusText = document.getElementById('status-text');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const logContainer = document.getElementById('logContainer');
    const logContent = document.getElementById('logContent');
    
    // Toggle elements
    const autoLoginToggle = document.getElementById('autoLogin');
    const fastModeToggle = document.getElementById('fastMode');
    const showLogsToggle = document.getElementById('showLogs');
    
    let currentTab = null;
    
    // Initialize popup
    init();
    
    async function init() {
        // Get current tab
        const tabs = await chrome.tabs.query({active: true, currentWindow: true});
        currentTab = tabs[0];
        
        // Load settings
        await loadSettings();
        
        // Check page status
        await checkPageStatus();
        
        // Set up event listeners
        setupEventListeners();
    }
    
    async function loadSettings() {
        const settings = await chrome.storage.sync.get({
            autoLogin: true,
            fastMode: true,
            showLogs: false
        });
        
        setToggleState(autoLoginToggle, settings.autoLogin);
        setToggleState(fastModeToggle, settings.fastMode);
        setToggleState(showLogsToggle, settings.showLogs);
        
        // Show/hide logs based on setting
        logContainer.style.display = settings.showLogs ? 'block' : 'none';
    }
    
    function setToggleState(toggle, active) {
        if (active) {
            toggle.classList.add('active');
        } else {
            toggle.classList.remove('active');
        }
    }
    
    function setupEventListeners() {
        // Fill form button
        fillFormBtn.addEventListener('click', async () => {
            await startFormFilling();
        });
        
        // Login help button
        loginHelpBtn.addEventListener('click', async () => {
            await handleLoginComplete();
        });
        
        // Config button
        configBtn.addEventListener('click', () => {
            chrome.tabs.create({url: 'chrome-extension://' + chrome.runtime.id + '/config.html'});
        });
        
        // Reset button
        resetBtn.addEventListener('click', async () => {
            await resetSettings();
        });
        
        // Toggle listeners
        autoLoginToggle.addEventListener('click', () => toggleSetting('autoLogin', autoLoginToggle));
        fastModeToggle.addEventListener('click', () => toggleSetting('fastMode', fastModeToggle));
        showLogsToggle.addEventListener('click', () => toggleSetting('showLogs', showLogsToggle));
    }
    
    async function checkPageStatus() {
        try {
            const response = await chrome.tabs.sendMessage(currentTab.id, {
                action: 'checkStatus'
            });
            
            if (response.loginDetected) {
                showLoginDetected();
            } else if (response.isJobPage) {
                showJobPageReady();
            } else {
                showGenericPage();
            }
        } catch (error) {
            console.log('Content script not ready:', error);
            showGenericPage();
        }
    }
    
    function showLoginDetected() {
        statusDiv.className = 'status login-detected';
        statusText.textContent = '🔐 Login page detected';
        fillFormBtn.style.display = 'none';
        loginHelpBtn.style.display = 'block';
    }
    
    function showJobPageReady() {
        statusDiv.className = 'status ready';
        statusText.textContent = '✅ Job application page ready';
        fillFormBtn.style.display = 'block';
        loginHelpBtn.style.display = 'none';
    }
    
    function showGenericPage() {
        statusDiv.className = 'status';
        statusText.textContent = '🌐 Navigate to a job application page';
        fillFormBtn.style.display = 'block';
        loginHelpBtn.style.display = 'none';
    }
    
    async function startFormFilling() {
        fillFormBtn.disabled = true;
        fillFormBtn.textContent = '⚡ Filling form...';
        progressContainer.style.display = 'block';
        
        try {
            const settings = await chrome.storage.sync.get({
                fastMode: true,
                showLogs: false
            });
            
            const response = await chrome.tabs.sendMessage(currentTab.id, {
                action: 'fillForm',
                settings: settings
            });
            
            if (response.success) {
                showProgress(100);
                addLog('✅ Form filled successfully!', 'success');
                fillFormBtn.textContent = '✅ Form Filled!';
                
                setTimeout(() => {
                    fillFormBtn.disabled = false;
                    fillFormBtn.textContent = '⚡ Fill Application Form';
                    progressContainer.style.display = 'none';
                }, 3000);
                
            } else {
                addLog('❌ Form filling failed: ' + response.error, 'error');
                fillFormBtn.disabled = false;
                fillFormBtn.textContent = '❌ Fill Failed - Retry';
                progressContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Form filling error:', error);
            addLog('❌ Extension error: ' + error.message, 'error');
            fillFormBtn.disabled = false;
            fillFormBtn.textContent = '❌ Error - Retry';
            progressContainer.style.display = 'none';
        }
    }
    
    async function handleLoginComplete() {
        loginHelpBtn.disabled = true;
        loginHelpBtn.textContent = '🔄 Checking...';
        
        try {
            const response = await chrome.tabs.sendMessage(currentTab.id, {
                action: 'checkPostLogin'
            });
            
            if (response.loginComplete) {
                showJobPageReady();
                addLog('✅ Login successful! Ready to fill form.', 'success');
            } else {
                addLog('⚠️ Still on login page. Please complete login first.', 'warning');
                loginHelpBtn.disabled = false;
                loginHelpBtn.textContent = '🔐 Login Detected - Click After Login';
            }
        } catch (error) {
            console.error('Login check error:', error);
            addLog('❌ Login check failed: ' + error.message, 'error');
            loginHelpBtn.disabled = false;
            loginHelpBtn.textContent = '🔐 Login Detected - Click After Login';
        }
    }
    
    function showProgress(percent) {
        progressBar.style.width = percent + '%';
    }
    
    function addLog(message, type = 'info') {
        const settings = chrome.storage.sync.get({showLogs: false});
        if (!settings.showLogs) return;
        
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logContent.appendChild(entry);
        
        // Auto-scroll to bottom
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Keep only last 50 entries
        while (logContent.children.length > 50) {
            logContent.removeChild(logContent.firstChild);
        }
    }
    
    async function toggleSetting(key, toggle) {
        const isActive = toggle.classList.contains('active');
        
        if (isActive) {
            toggle.classList.remove('active');
        } else {
            toggle.classList.add('active');
        }
        
        await chrome.storage.sync.set({[key]: !isActive});
        
        // Handle special cases
        if (key === 'showLogs') {
            logContainer.style.display = !isActive ? 'block' : 'none';
        }
    }
    
    async function resetSettings() {
        await chrome.storage.sync.clear();
        await loadSettings();
        addLog('⚙️ Settings reset to defaults', 'info');
    }
    
    // Listen for messages from content script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'updateProgress') {
            showProgress(message.percent);
        } else if (message.action === 'log') {
            addLog(message.message, message.type);
        } else if (message.action === 'statusUpdate') {
            if (message.status === 'loginDetected') {
                showLoginDetected();
            } else if (message.status === 'ready') {
                showJobPageReady();
            }
        }
    });
});