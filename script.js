console.log('Script.js loaded');

let maxRetries = 10;
let retryCount = 0;

function initializeApp() {
    console.log('Checking Telegram WebApp environment, attempt:', retryCount + 1);
    if (window.Telegram && window.Telegram.WebApp) {
        console.log('✅ Running in Telegram WebApp environment');
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        initializeTONConnect();
    } else {
        console.error('❌ Not running in Telegram WebApp environment');
        document.getElementById('status').textContent = 'Error: This app must be run inside Telegram';
        if (retryCount < maxRetries) {
            retryCount++;
            setTimeout(initializeApp, 1000);
        } else {
            console.error('Max retries reached. Telegram WebApp not detected.');
            document.getElementById('status').textContent = 'Error: Could not detect Telegram WebApp after multiple attempts';
        }
    }
}

function initializeTONConnect() {
    console.log('Initializing TONConnectUI');
    if (typeof TonConnectUI === 'undefined') {
        console.error('❌ TONConnectUI is not defined. Check if the SDK script loaded correctly.');
        document.getElementById('status').textContent = 'Error: TON Connect SDK not loaded';
        return;
    }

    try {
        const tonConnectUI = new TonConnectUI({
            manifestUrl: '/tonconnect-manifest.json',
            buttonRootId: 'connect-wallet'
        });
        console.log('✅ TONConnectUI initialized successfully');

        tonConnectUI.onStatusChange(wallet => {
            console.log('Wallet status changed:', wallet);
            if (wallet) {
                document.getElementById('wallet-address').textContent = `Wallet: ${wallet.account.address}`;
                document.getElementById('send-transaction').disabled = false;
                fetchBalance(wallet.account.address);
            } else {
                document.getElementById('wallet-address').textContent = 'Wallet: Not connected';
                document.getElementById('balance').textContent = 'Balance: 0 TON';
                document.getElementById('send-transaction').disabled = true;
            }
        });

        document.getElementById('connect-wallet').addEventListener('click', () => {
            console.log('Connect wallet button clicked');
        });

        document.getElementById('send-transaction').addEventListener('click', async () => {
            console.log('Send transaction clicked');
            try {
                const transaction = {
                    validUntil: Math.floor(Date.now() / 1000) + 60,
                    messages: [
                        {
                            address: 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c',
                            amount: '1000000000' // 1 TON
                        }
                    ]
                };
                await tonConnectUI.sendTransaction(transaction);
                document.getElementById('status').textContent = 'Transaction sent!';
                const response = await fetch('/send_transaction', { method: 'POST', body: JSON.stringify({}) });
                console.log(await response.json());
            } catch (error) {
                console.error('Error sending transaction:', error);
                document.getElementById('status').textContent = 'Error: ' + error.message;
            }
        });

    } catch (error) {
        console.error('Error initializing TONConnectUI:', error);
        document.getElementById('status').textContent = 'Error initializing TON Connect: ' + error.message;
    }
}

async function fetchBalance(address) {
    console.log('Fetching balance for:', address);
    try {
        const response = await fetch('/get_balance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_address: address })
        });
        const data = await response.json();
        if (data.balance) {
            document.getElementById('balance').textContent = `Balance: ${data.balance} TON`;
        } else {
            document.getElementById('balance').textContent = 'Error fetching balance: ' + (data.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Error fetching balance:', error);
        document.getElementById('balance').textContent = 'Error fetching balance';
    }
}

window.addEventListener('load', initializeApp);
