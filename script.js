let tonConnectUI = null;

function isTelegramWebApp() {
    // تحقق شامل من وجود WebApp Telegram
    return (window.Telegram && window.Telegram.WebApp && 
            window.Telegram.WebApp.initData && 
            window.Telegram.WebApp.initDataUnsafe);
}

function initializeApp() {
    if (isTelegramWebApp()) {
        // تم الكشف عن بيئة Telegram
        document.getElementById('app-container').style.display = 'block';
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        initializeTONConnect();
    } else {
        // ليس داخل Telegram - إظهار رسالة الخطأ
        document.getElementById('telegram-error').style.display = 'block';
        document.getElementById('app-container').style.display = 'none';
    }
}

function initializeTONConnect() {
    if (typeof TONConnectUI === 'undefined') {
        document.getElementById('status').textContent =
            '❌ TON Connect SDK لم يتم تحميله.';
        return;
    }

    tonConnectUI = new TONConnectUI({
        manifestUrl: window.location.origin + '/tonconnect-manifest.json',
        buttonRootId: 'connect-wallet'
    });

    tonConnectUI.onStatusChange(wallet => {
        if (wallet) {
            const shortAddress = wallet.account.address.substring(0, 6) + '...' + wallet.account.address.substring(wallet.account.address.length - 4);
            document.getElementById('wallet-address').textContent = `Wallet: ${shortAddress}`;
            document.getElementById('send-transaction').disabled = false;
            fetchBalance(wallet.account.address);
        } else {
            document.getElementById('wallet-address').textContent = 'Wallet: Not connected';
            document.getElementById('balance').textContent = 'Balance: 0 TON';
            document.getElementById('send-transaction').disabled = true;
        }
    });

    document.getElementById('send-transaction').addEventListener('click', async () => {
        if (!tonConnectUI.connected) {
            document.getElementById('status').textContent = 'Please connect wallet first';
            return;
        }
        
        const transaction = {
            validUntil: Math.floor(Date.now() / 1000) + 60,
            messages: [
                {
                    address: 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c',
                    amount: '1000000000'
                }
            ]
        };
        
        try {
            const result = await tonConnectUI.sendTransaction(transaction);
            document.getElementById('status').textContent = 'Transaction sent successfully!';
            console.log('Transaction result:', result);
        } catch (error) {
            console.error('Transaction error:', error);
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
        const data = await response.json();
        if (data.balance !== undefined) {
            document.getElementById('balance').textContent = `Balance: ${data.balance.toFixed(2)} TON`;
        } else if (data.error) {
            document.getElementById('balance').textContent = 'Error: ' + data.error;
        }
    } catch (error) {
        console.error('Balance fetch error:', error);
        document.getElementById('balance').textContent = 'Network error';
    }
}

// تهيئة التطبيق بعد تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // إعطاء وقت إضافي لتحميل بيئة Telegram
    setTimeout(initializeApp, 1000);
});
