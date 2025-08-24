from flask import Flask, render_template_string, request, jsonify, send_file
import requests
import os

app = Flask(__name__)

# ... (نفس INDEX_HTML أعلاه) ...

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

# إضافة路由 للصفحات الأساسية
@app.route('/terms')
def terms():
    return "شروط الاستخدام: هذا التطبيق يستخدم محفظة Telegram الداخلية"

@app.route('/privacy')
def privacy():
    return "سياسة الخصوصية: لا يتم تخزين أي بيانات شخصية"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
