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
    <link rel="stylesheet" href="/style.css">
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

    <div id="telegram-error" style="display:none; text-align:center; color:red;">
        ❌ Please open this app inside Telegram
    </div>

    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="/script.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

# خدمة ملفات JS و CSS
@app.route('/script.js')
def serve_js():
    return send_file('script.js')

@app.route('/style.css')
def serve_css():
    return send_file('style.css')

# TON Connect Manifest
@app.route('/tonconnect-manifest.json')
def serve_manifest():
    try:
        return send_file('tonconnect-manifest.json')
    except FileNotFoundError:
        return jsonify({
            "url": "https://yourdomain.com/",
            "name": "SYRX App", 
            "iconUrl": "https://yourdomain.com/icon.png",
            "termsOfUseUrl": "https://yourdomain.com/terms",
            "privacyPolicyUrl": "https://yourdomain.com/privacy"
        })

@app.route('/icon.png')
def serve_icon():
    return send_file('icon.png')

@app.route('/terms')
def terms():
    return "Terms of Use: This app connects to TON wallet"

@app.route('/privacy') 
def privacy():
    return "Privacy Policy: No user data is stored"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
