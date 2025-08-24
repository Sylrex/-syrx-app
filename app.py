from flask import Flask, render_template_string, request, jsonify, send_file
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
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
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
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        p {
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        #status {
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 SYRX App</h1>
        <div id="connect-wallet" style="margin: 20px 0;"></div>
        <p id="wallet-address">Wallet: Not connected</p>
        <p id="balance">Balance: 0 TON</p>
        <button id="send-transaction" disabled>Send 1 TON</button>
        <p id="status">Status: Loading...</p>
    </div>

    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="/tonconnect-ui.min.js"></script>
    <script>
        let tonConnectUI = null;

        function initializeApp() {
            console.log('🔍 Initializing app...');
            
            if (window.Telegram && window.Telegram.WebApp) {
                console.log('✅ Telegram WebApp detected');
                
                window.Telegram.WebApp.ready();
                window.Telegram.WebApp.expand();
                
                initializeTONConnect();
            } else {
                console.log('❌ Not in Telegram');
                document.getElementById('status').textContent = 'Please open in Telegram app';
            }
        }

        function initializeTONConnect() {
            console.log('🔄 Checking TON Connect...');
            
            if (typeof TONConnectUI === 'undefined') {
                console.log('❌ TONConnectUI not defined');
                document.getElementById('status').textContent = 'TON Connect not loaded';
                return;
            }

            try {
                console.log('✅ TONConnectUI found, initializing...');
                
                tonConnectUI = new TONConnectUI({
                    manifestUrl: window.location.origin + '/tonconnect-manifest.json',
                    buttonRootId: 'connect-wallet'
                });

                tonConnectUI.onStatusChange(function(wallet) {
                    if (wallet) {
                        const addr = wallet.account.address;
                        const shortAddr = addr.substring(0, 6) + '...' + addr.substring(addr.length - 4);
                        document.getElementById('wallet-address').textContent = 'Wallet: ' + shortAddr;
                        document.getElementById('send-transaction').disabled = false;
                        document.getElementById('status').textContent = 'Status: Connected ✅';
                    } else {
                        document.getElementById('wallet-address').textContent = 'Wallet: Not connected';
                        document.getElementById('send-transaction').disabled = true;
                        document.getElementById('status').textContent = 'Status: Ready to connect';
                    }
                });

                document.getElementById('send-transaction').addEventListener('click', function() {
                    if (!tonConnectUI.connected) {
                        document.getElementById('status').textContent = 'Please connect wallet first';
                        return;
                    }

                    const transaction = {
                        validUntil: Math.floor(Date.now() / 1000) + 60,
                        messages: [{
                            address: 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c',
                            amount: '1000000000'
                        }]
                    };

                    document.getElementById('status').textContent = 'Status: Signing...';
                    
                    tonConnectUI.sendTransaction(transaction)
                        .then(function() {
                            document.getElementById('status').textContent = 'Transaction sent! ✅';
                        })
                        .catch(function(error) {
                            document.getElementById('status').textContent = 'Error: ' + error.message;
                        });
                });

            } catch (error) {
                console.error('TON Connect error:', error);
                document.getElementById('status').textContent = 'Error: ' + error.message;
            }
        }

        // بدء التطبيق بعد تحميل الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initializeApp, 1000);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/SYRXApp')
def syrx_app():
    return render_template_string(INDEX_HTML)

@app.route('/tonconnect-ui.min.js')
def serve_tonconnect_js():
    try:
        return send_file('tonconnect-ui.min.js')
    except FileNotFoundError:
        return "TON Connect SDK not found", 404

@app.route('/tonconnect-manifest.json')
def serve_manifest():
    try:
        return send_file('tonconnect-manifest.json')
    except FileNotFoundError:
        return jsonify({
            "url": "https://syrx.onrender.com/SYRXApp",
            "name": "SYRX App", 
            "iconUrl": "https://syrx.onrender.com/icon.png"
        })

@app.route('/terms')
def terms():
    return "Terms of Use: This app connects to TON wallet"

@app.route('/privacy') 
def privacy():
    return "Privacy Policy: No user data is stored"

@app.route('/icon.png')
def serve_icon():
    try:
        return send_file('icon.png')
    except FileNotFoundError:
        return "Icon not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
