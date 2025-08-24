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
    <script src="/tonconnect-ui.min.js"></script>
</head>
<body>
    <div class="container" id="app-container" style="display:none;">
        <h1>Welcome to SYRX Mini App</h1>
        <button id="connect-wallet">Connect TON Wallet</button>
        <p id="wallet-address">Wallet: Not connected</p>
        <p id="balance">Balance: 0 TON</p>
        <button id="send-transaction" disabled>Send 1 TON</button>
        <p id="status"></p>
    </div>
    <div id="telegram-error" style="display:none; color:red; text-align:center; margin-top:50px;">
        ❌ الرجاء فتح هذا التطبيق من داخل تطبيق Telegram فقط
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

# ... بقية الرواتب بدون تغيير ...

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
        return jsonify({'balance': balance})
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
