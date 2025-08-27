from flask import Flask, send_file, render_template_string, Response
import os

app = Flask(__name__)

# تقديم index.html
@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            return render_template_string(file.read())
    except FileNotFoundError:
        return Response("خطأ: ملف index.html غير موجود", status=404)

# إعادة توجيه طلبات /SYRXApp إلى الجذر
@app.route('/SYRXApp')
def redirect_syrxapp():
    return Response("تم إعادة التوجيه إلى الصفحة الرئيسية", status=302, headers={"Location": "/"})

# تقديم tonconnect-manifest.json
@app.route('/tonconnect-manifest.json')
def serve_manifest():
    try:
        return send_file('tonconnect-manifest.json')
    except FileNotFoundError:
        return Response("خطأ: ملف tonconnect-manifest.json غير موجود", status=404)

# تقديم الملفات الثابتة
@app.route('/<path:filename>')
def serve_static(filename):
    try:
        if os.path.exists(filename):
            return send_file(filename)
        else:
            return Response(f"خطأ: الملف {filename} غير موجود", status=404)
    except Exception as e:
        return Response(f"خطأ: {str(e)}", status=500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # لدعم Render
    app.run(debug=False, host='0.0.0.0', port=port)
