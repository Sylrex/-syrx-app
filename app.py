from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='.')

# الصفحة الرئيسية
@app.route("/SYRXApp")
def home():
    return send_from_directory('.', 'index.html')

# أي ملف آخر تحت نفس المسار
@app.route("/SYRXApp/<path:filename>")
def serve_files(filename):
    return send_from_directory('.', filename)

if __name__ == "__main__":
    app.run(debug=True)
