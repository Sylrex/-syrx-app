from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='.')

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/<path:filename>")
def serve_files(filename):
    return send_from_directory('.', filename)

# مسار خاص للـ manifest
@app.route("/tonconnect-manifest.json")
def manifest():
    return send_from_directory('.', 'tonconnect-manifest.json')

if __name__ == "__main__":
    app.run(debug=True)
