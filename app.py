from flask import Flask, render_template_string, request, jsonify, send_file
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYRX Mini App</title>
    <link rel="stylesheet" href="/style.css">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://unpkg.com/@tonconnect/ui@latest/dist/tonconnect-ui.min.js"></script>
</head>
<body>
    <div class="container" id="app-container" style="display:none;">
        <h1>🚀 Welcome to SYRX Mini App</h1>
        <div id="connect-wallet" style="margin: 20px 0;"></div>
        <p id="wallet-address">Wallet: Not connected</p>
        <p id="balance">Balance: 0 TON</p>
        <button id="send-transaction" disabled>Send 1 TON</button>
        <p id="status">Status: Loading wallet system...</p>
    </div>
    
    <div class="telegram-error" id="telegram-error" style="display:none;">
        <h2>❌ Telegram App Required</h2>
        <p>Please open this application from within the Telegram app</p>
        <p><small>This mini-app only works inside Telegram Messenger</small></p>
    </div>

    <script src="/script.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/SYRXApp')
def syrx_app():
    return render_template_string(INDEX_HTML)

@app.route('/style.css')
def serve_css():
    return send_file('style.css')

@app.route('/script.js')
def serve_js():
    return send_file('script.js')

@app.route('/tonconnect-manifest.json')
def serve_manifest():
    return send_file('tonconnect-manifest.json')

@app.route('/icon.png')
def serve_icon():
    return send_file('icon.png')

@app.route('/terms')
def terms():
    return """
    <h1>Terms of Use</h1>
    <p>This application does not store any personal data. All transactions are on blockchain.</p>
    """

@app.route('/privacy')
def privacy():
    return """
    <h1>Privacy Policy</h1>
    <p>We respect your privacy. We do not collect or store any personal data.</p>
    """

@app.route('/get_balance', methods=['POST'])
def get_balance():
    try:
        data = request.json
        wallet_address = data.get('wallet_address')
        if not wallet_address:
            return jsonify({'error': 'No wallet address provided'}), 400
        
        response = requests.get(f'https://tonapi.io/v2/accounts/{wallet_address}')
        response.raise_for_status()
        account_data = response.json()
        
        balance = account_data.get('balance', 0) / 1e9
        return jsonify({'balance': round(balance, 4)})
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    return jsonify({'status': 'Transaction sent successfully'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
