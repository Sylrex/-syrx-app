from flask import Flask, render_template_string, request, jsonify, send_file, send_from_directory
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# إعدادات مهمة للملفات
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # لا تخزن ملفات مؤقتة

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
        <h1>🚀 Welcome to SYRX Mini App</h1>
        <div id="connect-wallet" style="margin: 20px 0;"></div>
        <p id="wallet-address">Wallet: Not connected</p>
        <p id="balance">Balance: 0 TON</p>
        <button id="send-transaction" disabled>Send 1 TON</button>
        <p id="status">Status: Loading...</p>
    </div>
    
    <div class="telegram-error" id="telegram-error" style="display:none;">
        <h2>❌ Telegram App Required</h2>
        <p>Please open this application from within the Telegram app</p>
    </div>

    <script src="/script.js"></script>
</body>
</html>
