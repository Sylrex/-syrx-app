from flask import Flask, send_file, render_template_string
import os

app = Flask(__name__)

# تقديم index.html
@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as file:
        return render_template_string(file.read())

# تقديم tonconnect-manifest.json
@app.route('/tonconnect-manifest.json')
def serve_manifest():
    return send_file('tonconnect-manifest.json')

# تقديم الملفات الثابتة (مثل icon.png, terms.html, privacy.html)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_file(filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render يستخدم متغير PORT
    app.run(debug=False, host='0.0.0.0', port=port)
