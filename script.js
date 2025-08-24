// script.js
let tonConnectUI = null;
let checkInterval = null;
let elapsed = 0;
const maxElapsed = 5000;

function initializeApp() {
    checkInterval = setInterval(() => {
        elapsed += 500;
        if (window.Telegram && window.Telegram.WebApp) {
            clearInterval(checkInterval);
            document.getElementById('app-container').style.display = 'block';
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
            initializeTONConnect();
        } else if (elapsed >= maxElapsed) {
            clearInterval(checkInterval);
            document.getElementById('telegram-error').style.display = 'block';
        }
    }, 500);
}

function initializeTONConnect() {
    if (typeof TONConnectUI === 'undefined') {
        document.getElementById('status').textContent =
            '❌ TON Connect SDK لم يتم تحميله.';
        return;
    }

    tonConnectUI = new TONConnectUI({
        manifestUrl: '/tonconnect-manifest.json',
        buttonRootId: 'connect-wallet'
    });

    tonConnectUI.onStatusChange(wallet => {
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

    document.getElementById('connect-wallet').addEventListener('click', () => {});
    document.getElementById('send-transaction').addEventListener('click', async () => {
        if (!tonConnectUI) return;
        const transaction = {
            validUntil: Math.floor(Date.now() / 1000) + 60,
            messages: [{ address: 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c', amount: '1000000000' }]
        };
        try {
            await tonConnectUI.sendTransaction(transaction);
            document.getElementById('status').textContent = 'Transaction sent!';
            await fetch('/send_transaction', { method: 'POST', body: JSON.stringify({}) });
        } catch (error) {
            document.getElementById('status').textContent = 'Error: ' + error.message;
        }
    });
}

window.addEventListener('load', initializeApp);

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
        } else {
            document.getElementById('balance').textContent = 'Error fetching balance';
        }
    } catch {
        document.getElementById('balance').textContent = 'Error fetching balance';
    }
    }
