from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

# قالب HTML مباشرة داخل الكود
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYRX-like Mini App</title>
    <link rel="stylesheet" href="style.css">
    <script src="https://unpkg.com/@tonconnect/ui@latest/dist/tonconnect-ui.min.js"></script>
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
    <script src="script.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/get_balance', methods=['POST'])
def get_balance():
    data = request.json
    wallet_address = data.get('wallet_address')
    if not wallet_address:
        return jsonify({'error': 'No wallet address provided'}), 400
    try:
        response = requests.get(f'https://tonapi.io/v2/accounts/{wallet_address}/balances')
        balance_data = response.json()
        balance = balance_data.get('balance', 0) / 1e9  # تحويل من nanoTON إلى TON
        return jsonify({'balance': balance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    return jsonify({'status': 'Transaction sent successfully'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render يستخدم PORT
    app.run(host='0.0.0.0', port=port, debug=True)
