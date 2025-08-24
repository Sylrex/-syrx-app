
### 3. ثالثاً: استخدم هذا الكود لـ `script.js`:

```javascript
let tonConnectUI = null;
let retryCount = 0;
const maxRetries = 5;

function isTelegramWebApp() {
    return (window.Telegram && window.Telegram.WebApp);
}

function checkTONConnectLoaded() {
    return typeof TONConnectUI !== 'undefined';
}

function initializeApp() {
    if (isTelegramWebApp()) {
        console.log('📱 Telegram WebApp detected');
        document.getElementById('app-container').style.display = 'block';
        document.getElementById('telegram-error').style.display = 'none';
        
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        
        // تحميل TON Connect مباشرة
        loadTONConnect();
    } else {
        console.log('❌ Not in Telegram environment');
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('telegram-error').style.display = 'block';
    }
}

function loadTONConnect() {
    // إذا كان محملاً بالفعل
    if (checkTONConnectLoaded()) {
        initializeTONConnect();
        return;
    }
    
    // إذا لم يكن محملاً، حاول تحميله
    document.getElementById('status').textContent = '🔄 Loading wallet system...';
    
    const script = document.createElement('script');
    script.src = '/tonconnect-ui.min.js?v=' + new Date().getTime(); // إضافة timestamp لمنع التخزين
    script.onload = () => {
        console.log('✅ TON Connect SDK loaded successfully');
        initializeTONConnect();
    };
    script.onerror = (error) => {
        console.error('❌ Failed to load TON Connect:', error);
        retryCount++;
        
        if (retryCount < maxRetries) {
            document.getElementById('status').textContent = `🔄 Retrying load... (${retryCount}/${maxRetries})`;
            setTimeout(loadTONConnect, 2000);
        } else {
            document.getElementById('status').textContent = '❌ Failed to load wallet after multiple attempts';
            showAlternativeOptions();
        }
    };
    
    document.head.appendChild(script);
}

function showAlternativeOptions() {
    const statusElement = document.getElementById('status');
    statusElement.innerHTML = `
        ❌ Wallet system unavailable<br>
        <small>Please try refreshing or check your connection</small>
        <button onclick="location.reload()" style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 5px; margin-top: 10px; cursor: pointer;">
            🔄 Refresh Page
        </button>
    `;
}

function initializeTONConnect() {
    if (!checkTONConnectLoaded()) {
        document.getElementById('status').textContent = '❌ TON Connect not loaded';
        return;
    }

    try {
        console.log('🔄 Initializing TON Connect...');
        document.getElementById('status').textContent = 'Status: Initializing...';
        
        tonConnectUI = new TONConnectUI({
            manifestUrl: window.location.origin + '/tonconnect-manifest.json',
            buttonRootId: 'connect-wallet',
            language: 'en'
        });

        tonConnectUI.onStatusChange(wallet => {
            if (wallet) {
                const shortAddress = wallet.account.address.substring(0, 6) + '...' + 
                                   wallet.account.address.substring(wallet.account.address.length - 4);
                document.getElementById('wallet-address').textContent = `Wallet: ${shortAddress}`;
                document.getElementById('send-transaction').disabled = false;
                document.getElementById('status').textContent = 'Status: Connected ✅';
            } else {
                document.getElementById('wallet-address').textContent = 'Wallet: Not connected';
                document.getElementById('balance').textContent = 'Balance: 0 TON';
                document.getElementById('send-transaction').disabled = true;
                document.getElementById('status').textContent = 'Status: Ready to connect';
            }
        });

        // إعداد زر الإرسال
        document.getElementById('send-transaction').addEventListener('click', async () => {
            if (!tonConnectUI?.connected) {
                document.getElementById('status').textContent = 'Please connect wallet first';
                return;
            }
            
            try {
                const transaction = {
                    validUntil: Math.floor(Date.now() / 1000) + 60,
                    messages: [{
                        address: 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c',
                        amount: '1000000000'
                    }]
                };
                
                document.getElementById('status').textContent = 'Status: Signing...';
                await tonConnectUI.sendTransaction(transaction);
                document.getElementById('status').textContent = 'Transaction sent! ✅';
                
            } catch (error) {
                document.getElementById('status').textContent = 'Error: ' + error.message;
            }
        });

    } catch (error) {
        console.error('TON Connect init error:', error);
        document.getElementById('status').textContent = 'Error: ' + error.message;
    }
}

// بدء التطبيق
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeApp, 1000);
});
