let tonConnectUI = null;

function isTelegramWebApp() {
    return (window.Telegram && window.Telegram.WebApp);
}

function initializeApp() {
    if (isTelegramWebApp()) {
        document.getElementById('app-container').style.display = 'block';
        document.getElementById('telegram-error').style.display = 'none';
        
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        
        initializeTONConnect();
    } else {
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('telegram-error').style.display = 'block';
    }
}

function initializeTONConnect() {
    // انتظر قليلاً لتحميل TONConnectUI
    setTimeout(() => {
        if (typeof TONConnectUI === 'undefined') {
            document.getElementById('status').textContent = '❌ Please wait, loading wallet...';
            setTimeout(initializeTONConnect, 1000);
            return;
        }

        try {
            tonConnectUI = new TONConnectUI({
                manifestUrl: window.location.origin + '/tonconnect-manifest.json',
                buttonRootId: 'connect-wallet'
            });

            tonConnectUI.onStatusChange(wallet => {
                if (wallet) {
                    const shortAddress = wallet.account.address.substring(0, 6) + '...' + 
                                       wallet.account.address.substring(wallet.account.address.length - 4);
                    document.getElementById('wallet-address').textContent = `Wallet: ${shortAddress}`;
                    document.getElementById('send-transaction').disabled = false;
                    document.getElementById('status').textContent = 'Status: Connected';
                    fetchBalance(wallet.account.address);
                }
            });

            document.getElementById('send-transaction').addEventListener('click', sendTransaction);

        } catch (error) {
            document.getElementById('status').textContent = 'Error: ' + error.message;
        }
    }, 500);
}

async function sendTransaction() {
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
        
        await tonConnectUI.sendTransaction(transaction);
        document.getElementById('status').textContent = 'Transaction sent!';
        
    } catch (error) {
        document.getElementById('status').textContent = 'Error: ' + error.message;
    }
}

async function fetchBalance(address) {
    try {
        const response = await fetch('/get_balance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_address: address })
        });
        const data = await response.json();
        if (data.balance) {
            document.getElementById('balance').textContent = `Balance: ${data.balance} TON`;
        }
    } catch (error) {
        console.error('Balance error:', error);
    }
}

// بدء التطبيق
setTimeout(initializeApp, 1000);
