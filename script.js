let tonConnectUI = null;

function initializeApp() {
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        initializeTONConnect();
    } else {
        document.body.innerHTML = `
            <div style="font-family: Arial; text-align: center; margin-top: 50px;">
                <h2>❌ الرجاء فتح هذا التطبيق من داخل تطبيق Telegram فقط</h2>
            </div>
        `;
    }
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

    document.getElementById('connect-wallet').addEventListener('click', () => {
        console.log('Connect wallet clicked');
    });

    document.getElementById('send-transaction').addEventListener('click', async () => {
        if (!tonConnectUI) return;
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
            await tonConnectUI.sendTransaction(transaction);
            document.getElementById('status').textContent = 'Transaction sent!';
            await fetch('/send_transaction', { method: 'POST', body: JSON.stringify({}) });
        } catch (error) {
            document.getElementById('status').textContent = 'Error: ' + error.message;
        }
    });
}

window.addEventListener('load', initializeApp);
