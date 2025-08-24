// script.js
let tonConnectUI = null;

function isTelegramWebApp() {
    return (window.Telegram && 
            window.Telegram.WebApp && 
            window.Telegram.WebApp.initData && 
            window.Telegram.WebApp.initDataUnsafe &&
            window.Telegram.WebApp.platform);
}

function loadTONConnectSDK() {
    return new Promise((resolve, reject) => {
        if (typeof TONConnectUI !== 'undefined') {
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://unpkg.com/@tonconnect/ui@latest/dist/tonconnect-ui.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

async function initializeApp() {
    if (isTelegramWebApp()) {
        try {
            console.log('Telegram WebApp detected');
            document.getElementById('app-container').style.display = 'block';
            document.getElementById('telegram-error').style.display = 'none';
            
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
            
            document.getElementById('status').textContent = 'Status: Loading wallet SDK...';
            await loadTONConnectSDK();
            
            initializeTONConnect();
            
        } catch (error) {
            console.error('Failed to load TON Connect SDK:', error);
            document.getElementById('status').textContent = '❌ Failed to load wallet system. Please refresh.';
        }
    } else {
        console.log('Not in Telegram environment');
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('telegram-error').style.display = 'block';
    }
}

function initializeTONConnect() {
    const connectButton = document.getElementById('connect-wallet');
    if (!connectButton) {
        document.getElementById('status').textContent = 'Error: Connect element missing';
        return;
    }

    if (typeof TONConnectUI === 'undefined') {
        document.getElementById('status').textContent = '❌ Wallet SDK not available';
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
                document.getElementById('status').textContent = 'Status: Ready to connect';
            }
        });

        document.getElementById('send-transaction').addEventListener('click', async () => {
            if (!tonConnectUI || !tonConnectUI.connected) {
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
                document.getElementById('status').textContent = 'Status: Signing transaction...';
                await tonConnectUI.sendTransaction(transaction);
                document.getElementById('status').textContent = 'Status: Transaction sent successfully!';
                
                if (tonConnectUI.wallet) {
                    setTimeout(() => fetchBalance(tonConnectUI.wallet.account.address), 2000);
                }
                
            } catch (error) {
                console.error('Transaction error:', error);
                document.getElementById('status').textContent = 'Error: ' + error.message;
            }
        });

    } catch (error) {
        console.error('TON Connect initialization error:', error);
        document.getElementById('status').textContent = 'Error initializing wallet: ' + error.message;
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

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeApp, 100);
});
