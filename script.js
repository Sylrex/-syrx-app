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
        document.getElementById('app-container').style.display = 'block';
        document.getElementById('telegram-error').style.display = 'none';
        
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        
        loadTONConnect();
    } else {
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('telegram-error').style.display = 'block';
    }
}

function loadTONConnect() {
    if (checkTONConnectLoaded()) {
        initializeTONConnect();
        return;
    }
    
    document.getElementById('status').textContent = '🔄 Loading wallet system...';
    
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/@tonconnect/ui@latest/dist/tonconnect-ui.min.js';
    script.onload = () => initializeTONConnect();
    script.onerror = () => {
        retryCount++;
        if (retryCount < maxRetries) {
            document.getElementById('status').textContent = `🔄 Retrying load... (${retryCount}/${maxRetries})`;
            setTimeout(loadTONConnect, 2000);
        } else {
            document.getElementById('status').textContent = '❌ Failed to load wallet after multiple attempts';
        }
    };
    
    document.head.appendChild(script);
}

function initializeTONConnect() {
    if (!checkTONConnectLoaded()) {
        document.getElementById('status').textContent = '❌ TON Connect not loaded';
        return;
    }

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

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeApp, 1000);
});
