let tonConnectUI = null;
let retryCount = 0;
const maxRetries = 10;

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
        
        startTONConnectCheck();
    } else {
        console.log('❌ Not in Telegram environment');
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('telegram-error').style.display = 'block';
    }
}

function startTONConnectCheck() {
    const checkInterval = setInterval(() => {
        if (checkTONConnectLoaded()) {
            clearInterval(checkInterval);
            console.log('✅ TON Connect SDK loaded successfully');
            initializeTONConnect();
        } else {
            retryCount++;
            document.getElementById('status').textContent = `⏳ Loading wallet... (${retryCount}/${maxRetries})`;
            
            if (retryCount >= maxRetries) {
                clearInterval(checkInterval);
                document.getElementById('status').textContent = '❌ Failed to load wallet. Please refresh the page.';
                showManualLoadButton();
            }
        }
    }, 1000);
}

function showManualLoadButton() {
    const statusElement = document.getElementById('status');
    statusElement.innerHTML = '❌ Wallet failed to load. ' +
        '<button onclick="manualLoadTONConnect()" style="background: #007bff; color: white; border: none; padding: 5px 10px; border-radius: 3px; margin-left: 10px;">Retry Load</button>';
}

function manualLoadTONConnect() {
    document.getElementById('status').textContent = '🔄 Manually loading wallet...';
    retryCount = 0;
    
    // محاولة تحميل يدوي
    const script = document.createElement('script');
    script.src = '/tonconnect-ui.min.js';
    script.onload = () => {
        console.log('✅ Manual load successful');
        initializeTONConnect();
    };
    script.onerror = () => {
        document.getElementById('status').textContent = '❌ Manual load failed. Check server.';
    };
    document.head.appendChild(script);
}

function initializeTONConnect() {
    if (!checkTONConnectLoaded()) {
        document.getElementById('status').textContent = '❌ TON Connect still not loaded';
        return;
    }

    try {
        console.log('🔄 Initializing TON Connect...');
        document.getElementById('status').textContent = 'Status: Connecting...';
        
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
                fetchBalance(wallet.account.address);
            } else {
                updateDisconnectedState();
            }
        });

        setupSendButton();

    } catch (error) {
        console.error('TON Connect init error:', error);
        document.getElementById('status').textContent = 'Error: ' + error.message;
    }
}

function updateDisconnectedState() {
    document.getElementById('wallet-address').textContent = 'Wallet: Not connected';
    document.getElementById('balance').textContent = 'Balance: 0 TON';
    document.getElementById('send-transaction').disabled = true;
    document.getElementById('status').textContent = 'Status: Ready to connect';
}

function setupSendButton() {
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
}

async function fetchBalance(address) {
    try {
        const response = await fetch('/get_balance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_address: address })
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('balance').textContent = `Balance: ${data.balance || 0} TON`;
        }
    } catch (error) {
        console.log('Balance check failed:', error);
    }
}

// بدء التطبيق بعد تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeApp, 500);
});
