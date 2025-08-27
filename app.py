from flask import Flask, send_file, render_template_string, Response
import os

app = Flask(__name__)

# Serve index.html
@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            return render_template_string(file.read())
    except FileNotFoundError:
        return Response("Error: index.html not found", status=404)

# Redirect /SYRXApp to root
@app.route('/SYRXApp')
def redirect_syrxapp():
    return Response("Redirecting to homepage", status=302, headers={"Location": "/"})

# Serve tonconnect-manifest.json
@app.route('/tonconnect-manifest.json')
def serve_manifest():
    try:
        return send_file('tonconnect-manifest.json')
    except FileNotFoundError:
        return Response("Error: tonconnect-manifest.json not found", status=404)

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    try:
        if os.path.exists(filename):
            return send_file(filename)
        else:
            return Response(f"Error: File {filename} not found", status=404)
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # For Render
    app.run(debug=False, host='0.0.0.0', port=port)
