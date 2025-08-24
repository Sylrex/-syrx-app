console.log('Script.js loaded');
const tonConnectUI = new TONConnectUI({
    manifestUrl: 'https://syrx.onrender.com/tonconnect-manifest.json',
    buttonRootId: 'connect-wallet'
});

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
