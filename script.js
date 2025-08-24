let tonConnectUI = null;

function isTelegramWebApp() {
    // تحقق شامل من وجود WebApp Telegram
    return (window.Telegram && 
            window.Telegram.WebApp && 
            window.Telegram.WebApp.initData && 
            window.Telegram.WebApp.initDataUnsafe &&
            window.Telegram.WebApp.platform);
}

function initializeApp() {
    if (isTelegramWebApp()) {
        // تم الكشف عن بيئة Telegram
        console.log('Telegram WebApp detected');
        document.getElementById('app-container').style.display = 'block';
        document.getElementById('telegram-error').style.display = 'none';
        
        // تهيئة Telegram WebApp
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        
        // تهيئة TON Connect
        initializeTONConnect();
    } else {
        // ليس داخل Telegram - إظهار رسالة الخطأ
        console.log('Not in Telegram environment');
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('telegram-error').style.display = 'block';
    }
}

function initializeTONConnect() {
    if (typeof TONConnectUI === 'undefined') {
        document.getElementById('status').textContent = '❌ TON Connect SDK not loaded';
        return;
    }

    try {
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
                document.getElementById('status').textContent = 'Status: Connected';
                fetchBalance(wallet.account.address);
            } else {
                document.getElementById('wallet-address').textContent = 'Wallet: Not connected';
                document.getElementById('balance').textContent = 'Balance: 0 TON';
                document.getElementById('send-transaction').disabled = true;
                document.getElementById('status').textContent = 'Status: Disconnected';
            }
        });

        // إعداد معاملة الإرسال
        document.getElementById('send-transaction').addEventListener('click', sendTransaction);

    } catch (error) {
        console.error('TON Connect initialization error:', error);
        document.getElementById('status').textContent = 'Error initializing wallet';
    }
}

async function sendTransaction() {
    if (!tonConnectUI || !tonConnectUI.connected) {
        document.getElementById('status').textContent = 'Please connect wallet first';
        return;
    }
    
    try {
        const transaction = {
            validUntil: Math.floor(Date.now() / 1000) + 300, // 5 دقائق
            messages: [
                {
                    address: 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c', // عنوان تجريبي
                    amount: '1000000000' // 1 TON
                }
            ]
        };
        
        document.getElementById('status').textContent = 'Status: Signing transaction...';
        const result = await tonConnectUI.sendTransaction(transaction);
        
        document.getElementById('status').textContent = 'Status: Transaction sent successfully!';
        console.log('Transaction result:', result);
        
        // تحديث الرصيد بعد المعاملة
        if (tonConnectUI.wallet) {
            setTimeout(() => fetchBalance(tonConnectUI.wallet.account.address), 3000);
        }
        
    } catch (error) {
        console.error('Transaction error:', error);
        document.getElementById('status').textContent = 'Error: ' + (error.message || 'Transaction failed');
    }
}

async function fetchBalance(address) {
    try {
        document.getElementById('status').textContent = 'Status: Fetching balance...';
        const response = await fetch('/get_balance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_address: address })
        });
        
        const data = await response.json();
        if (data.balance !== undefined) {
            document.getElementById('balance').textContent = `Balance: ${data.balance} TON`;
            document.getElementById('status').textContent = 'Status: Balance updated';
        } else if (data.error) {
            document.getElementById('balance').textContent = 'Balance: Error';
            document.getElementById('status').textContent = 'Error: ' + data.error;
        }
    } catch (error) {
        console.error('Balance fetch error:', error);
        document.getElementById('balance').textContent = 'Balance: Network error';
        document.getElementById('status').textContent = 'Status: Network error';
    }
}

// تهيئة التطبيق بعد تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // إعطاء وقت لتحميل بيئة Telegram
    setTimeout(initializeApp, 100);
});
