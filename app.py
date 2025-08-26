from flask import Flask, render_template_string, send_file, jsonify
import os

app = Flask(__name__)

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYRX App</title>
    <style>
        body {
            font-family: Arial;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            width: 100%;
            max-width: 400px;
        }
        h1 { color: #333; margin-bottom: 20px; }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            margin: 10px 0;
            cursor: pointer;
            border-radius: 6px;
            width: 100%;
            font-size: 16px;
        }
        button:disabled { background: #ccc; cursor: not-allowed; }
        p { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 6px; }
        #status { color: #666; font-style: italic; }
        #telegram-error { display:none; text-align:center; color:red; }
    </style>
</head>
<body>
    <div class="container" id="app-container">
        <h1>🚀 SYRX App</h1>
        <div id="connect-wallet" style="margin: 20px 0;"></div>
        <p id="wallet-address">Wallet: Not connected</p>
        <p id="balance">Balance: 0 TON</p>
        <button id="send-transaction" disabled>Send 1 TON</button>
        <p id="status">Status: Loading...</p>
    </div>
    <div id="telegram-error">
        ❌ Please open this app inside Telegram
    </div>

    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://unpkg.com/@tonconnect/ui@latest/dist/tonconnect-ui.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            if (!window.Telegram || !window.Telegram.WebApp) {
                document.getElementById('app-container').style.display = 'none';
                document.getElementById('telegram-error').style.display = 'block';
                return;
            }

            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
            document.getElementById('app-container').style.display = 'block';

            if (typeof TONConnectUI === 'undefined') {
                document.getElementById('status').textContent = '❌ TON Connect not loaded';
                return;
            }

            const tonConnectUI = new TONConnectUI({
                manifestUrl: window.location.origin + '/tonconnect-manifest.json',
                buttonRootId: 'connect-wallet',
                language: 'en'
            });

            tonConnectUI.onStatusChange(wallet => {
                if (wallet) {
                    const addr = wallet.account.address;
                    const shortAddr = addr.slice(0,6) + '...' + addr.slice(-4);
                    document.getElementById('wallet-address').textContent = `Wallet: ${shortAddr}`;
                    document.getElementById('send-transaction').disabled = false;
                    document.getElementById('status').textContent = 'Status: Connected ✅';
                } else {
                    document.getElementById('wallet-address').textContent = 'Wallet: Not connected';
                    document.getElementById('balance').textContent = 'Balance: 0 TON';
                    document.getElementById('send-transaction').disabled = true;
                    document.getElementById('status').textContent = 'Status: Ready to connect';
                }
            });

            document.getElementById('send-transaction').onclick = async () => {
                if (!tonConnectUI.connected) {
                    document.getElementById('status').textContent = 'Please connect wallet first';
                    return;
                }
                try {
                    await tonConnectUI.sendTransaction({
                        validUntil: Math.floor(Date.now()/1000)+60,
                        messages: [{
                            address: 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c',
                            amount: '1000000000'
                        }]
                    });
                    document.getElementById('status').textContent = 'Transaction sent! ✅';
                } catch(e) {
                    document.getElementById('status').textContent = 'Error: ' + e.message;
                }
            };
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(INDEX_HTML)
@app.route('/SYRXApp') def syrx_app(): return render_template_string(INDEX_HTML)

@app.route('/tonconnect-manifest.json')
def serve_manifest():
    return jsonify({
        "url": "https://syrx.onrender.com/SYRXApp",
        "name": "SYRX App",
        "iconUrl": "https://syrx.onrender.com/icon.png",
        "termsOfUseUrl": "https://syrx.onrender.com/terms",
        "privacyPolicyUrl": "https://syrx.onrender.com/privacy"
    })

@app.route('/icon.png')
def serve_icon(): return send_file('icon.png')
@app.route('/terms') def terms(): return "Terms of Use: This app connects to TON wallet"
@app.route('/privacy') def privacy(): return "Privacy Policy: No user data is stored"

if __name__ == '__main__':
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port, debug=True)
