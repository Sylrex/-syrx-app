from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

# إعداد قاعدة بيانات SQLite
def init_db():
    conn = sqlite3.connect('syrx.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY, points INTEGER DEFAULT 0, wallet_address TEXT)''')
    conn.commit()
    conn.close()

init_db()

# جلب النقاط
@app.route('/api/points/<user_id>', methods=['GET'])
def get_points(user_id):
    conn = sqlite3.connect('syrx.db')
    c = conn.cursor()
    c.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    points = result[0] if result else 0
    return jsonify({'points': points})

# حفظ عنوان المحفظة
@app.route('/api/wallet/<user_id>', methods=['POST'])
def save_wallet(user_id):
    data = request.json
    wallet_address = data.get('wallet_address')
    if wallet_address:
        conn = sqlite3.connect('syrx.db')
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO users (user_id, points, wallet_address) VALUES (?, ?, ?)',
                  (user_id, 0, wallet_address))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
