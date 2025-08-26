let tonConnectUI = null;

function isTelegramWebApp() {
    return (window.Telegram && window.Telegram.WebApp);
}

function initializeApp() {
    if (!isTelegramWebApp()) {
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('telegram-error').style.display = 'block';
        return;
    }

    document.getElementById('app-container').style.display = 'block';
    document.getElementById('telegram-error').style.display = 'none';

    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();

    if (typeof TONConnectUI === 'undefined') {
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
            const shortAddress = wallet.account.address.substring(0, 6) + '...' + wallet.account.address.slice(-4);
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

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});
