from flask import Flask, render_template_string, request, jsonify, send_file
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYRX Mini App</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="icon" type="image/x-icon" href="data:image/x-icon;base64,AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAA/4QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEREQAAAAAAEAAAEAAAAAEAAAQAAAAAQAAABAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAQAAAQAAAAEAAAQAAAAAQAAAEAAAAAEAAAQAAAAAAAAAAAAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA">
    <!-- ✅ مكتبة تيليجرام -->
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="/tonconnect-ui.min.js" defer></script>
</head>
<body>
    <div class="container">
        <h1>Welcome to SYRX Mini App</h1>
        <button id="connect-wallet">Connect TON Wallet</button>
        <p id="wallet-address">Wallet: Not connected</p>
        <p id="balance">Balance: 0 TON</p>
        <button id="send-transaction" disabled>Send 1 TON</button>
        <p id="status"></p>
    </div>
    <script>
        window.addEventListener("load", () => {
            if (window.Telegram && window.Telegram.WebApp) {
                Telegram.WebApp.ready();
                Telegram.WebApp.expand();
                console.log("✅ Running inside Telegram WebApp");
            } else {
                document.getElementById("status").textContent = "⚠️ Please open this app from inside Telegram.";
                console.error("Not running inside Telegram WebApp");
            }
        });
    </script>
    <script src="/script.js" defer></script>
</body>
</html>
"""

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template_string(INDEX_HTML)

@app.route('/SYRXApp')
def syrx_app():
    logger.info("Serving SYRXApp page")
    return index()

@app.route('/style.css')
def serve_css():
    logger.info("Serving style.css")
    try:
        return send_file('style.css')
    except FileNotFoundError:
        logger.error("style.css not found")
        return "CSS file not found", 404

@app.route('/script.js')
def serve_js():
    logger.info("Serving script.js")
    try:
        return send_file('script.js')
    except FileNotFoundError:
        logger.error("script.js not found")
        return "JS file not found", 404

@app.route('/tonconnect-manifest.json')
def serve_manifest():
    logger.info("Serving tonconnect-manifest.json")
    try:
        return send_file('tonconnect-manifest.json')
    except FileNotFoundError:
        logger.error("tonconnect-manifest.json not found")
        return "Manifest file not found", 404

@app.route('/tonconnect-ui.min.js')
def serve_tonconnect_js():
    logger.info("Serving tonconnect-ui.min.js")
    try:
        return send_file('tonconnect-ui.min.js')
    except FileNotFoundError:
        logger.error("tonconnect-ui.min.js not found")
        return "JavaScript file not found", 404

@app.route('/get_balance', methods=['POST'])
def get_balance():
    logger.info("Received get_balance request")
    data = request.json
    wallet_address = data.get('wallet_address')
    if not wallet_address:
        logger.error("No wallet address provided")
        return jsonify({'error': 'No wallet address provided'}), 400
    try:
        response = requests.get(f'https://tonapi.io/v2/accounts/{wallet_address}/balances')
        response.raise_for_status()
        balance_data = response.json()
        balance = balance_data.get('balance', 0) / 1e9
        logger.info(f"Balance fetched: {balance} TON")
        return jsonify({'balance': balance})
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    logger.info("Received send_transaction request")
    return jsonify({'status': 'Transaction sent successfully'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
