import os
from flask import Flask, render_template_string, send_from_directory, jsonify

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    <script src="/tonconnect-ui.min.js"></script>
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

# ✅ الملفات المحلية
@app.route('/script.js')
def serve_js():
    return send_from_directory(BASE_DIR, 'script.js')

@app.route('/style.css')
def serve_css():
    return send_from_directory(BASE_DIR, 'style.css')

@app.route('/tonconnect-ui.min.js')
def serve_tonconnect():
    return send_from_directory(BASE_DIR, 'tonconnect-ui.min.js')

@app.route('/tonconnect-manifest.json')
def serve_manifest():
    try:
        return send_from_directory(BASE_DIR, 'tonconnect-manifest.json')
    except FileNotFoundError:
        return jsonify({
            "url": "https://syrx.onrender.com/",
            "name": "SYRX App",
            "iconUrl": "https://syrx.onrender.com/icon.png",
            "termsOfUseUrl": "https://syrx.onrender.com/terms",
            "privacyPolicyUrl": "https://syrx.onrender.com/privacy"
        })

@app.route('/icon.png')
def serve_icon():
    return send_from_directory(BASE_DIR, 'icon.png')

@app.route('/terms')
def terms():
    return "Terms of Use: This app connects to TON wallet"

@app.route('/privacy')
def privacy():
    return "Privacy Policy: No user data is stored"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
