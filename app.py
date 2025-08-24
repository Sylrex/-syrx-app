from flask import Flask, render_template_string, request, jsonify, send_file
import requests
import os

app = Flask(__name__)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYRX Mini App</title>
    <link rel="stylesheet" href="/style.css">
    <script src="/tonconnect-ui.min.js"></script>
    <script src="/script.js"></script>
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

@app.route('/tonconnect-ui.min.js')
def serve_tonconnect_js():
    return send_file('tonconnect-ui.min.js')

@app.route('/tonconnect-manifest.json')
def serve_manifest():
    return send_file('tonconnect-manifest.json')

@app.route('/get_balance', methods=['POST'])
def get_balance():
    data = request.json
    wallet_address = data.get('wallet_address')
    if not wallet_address:
        return jsonify({'error': 'No wallet address provided'}), 400
    try:
        response = requests.get(f'https://tonapi.io/v2/accounts/{wallet_address}/balances')
        balance_data = response.json()
        balance = balance_data.get('balance', 0) / 1e9
        return jsonify({'balance': balance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    return jsonify({'status': 'Transaction sent successfully'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
