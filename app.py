from flask import Flask, render_template_string, request, jsonify, send_file
import os

app = Flask(__name__)

# أبسط HTML ممكن
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
        .telegram-error {
            color: red;
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            border: 2px solid #ff4444;
        }
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

    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script>
        // كود JavaScript مدمج مباشرة
        let tonConnectUI = null;

        function initializeApp() {
            console.log('🔍 Checking Telegram environment...');
            
            if (window.Telegram && window.Telegram.WebApp) {
                console.log('✅ Telegram WebApp detected');
                document.getElementById('status').textContent = 'Status: Telegram detected';
                
                window.Telegram.WebApp.ready();
                window.Telegram.WebApp.expand();
                
                loadTONConnect();
            } else {
                console.log('❌ Not in Telegram');
                document.getElementById('status').textContent = '❌ Please open in Telegram app';
            }
        }

        function loadTONConnect() {
            console.log('🔄 Loading TON Connect...');
            document.getElementById('status').textContent = 'Status: Loading wallet...';
            
            const script = document.createElement('script');
            script.src = '/tonconnect-ui.min.js?' + new Date().getTime();
            script.onload = function() {
                console.log('✅ TON Connect loaded');
                initializeTONConnect();
            };
            script.onerror = function() {
                console.log('❌ Failed to load TON Connect');
                document.getElementById('status').textContent = '❌ Wallet load failed. Refresh page.';
            };
            document.head.appendChild(script);
        }

        function initializeTONConnect() {
            if (typeof TONConnectUI === 'undefined') {
                document.getElementById('status').textContent = '❌ TON Connect not available';
                return;
            }

            try {
                tonConnectUI = new TONConnectUI({
                    manifestUrl: '/tonconnect-manifest.json',
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

            } catch (error) {
                document.getElementById('status').textContent = 'Error: ' + error.message;
            }
        }

        // بدء التطبيق
        setTimeout(initializeApp, 1000);
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
        return "File not found", 404

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
