let tonConnectUI;

function initializeApp() {
    let retries = 0;
    const maxRetries = 20;

    const interval = setInterval(() => {
        if (window.Telegram && window.Telegram.WebApp) {
            clearInterval(interval);
            document.getElementById('app-container').style.display = 'block';
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
            initializeTONConnect();
        } else {
            retries++;
            if (retries >= maxRetries) {
                clearInterval(interval);
                document.getElementById('telegram-error').style.display = 'block';
            }
        }
    }, 500);
}

function initializeTONConnect() {
    if (typeof TONConnectUI === 'undefined') {
        document.getElementById('status').textContent = 'Error: TON Connect SDK not loaded';
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

    document.getElementById('send-transaction').addEventListener('click', async () => {
        try {
            const transaction = {
                validUntil: Math.floor(Date.now() / 1000) + 60,
                messages: [{ address: 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c', amount: '1000000000' }]
            };
            await tonConnectUI.sendTransaction(transaction);
            document.getElementById('status').textContent = 'Transaction sent!';
            await fetch('/send_transaction', { method: 'POST', body: JSON.stringify({}) });
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

window.addEventListener('load', initializeApp);
