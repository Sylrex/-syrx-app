from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='.')

# الصفحة الرئيسية
@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

# أي ملف آخر في نفس المجلد
@app.route("/<path:filename>")
def serve_files(filename):
    return send_from_directory('.', filename)

if __name__ == "__main__":
    app.run(debug=True)
