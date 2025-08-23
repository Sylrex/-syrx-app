from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

# إعداد قاعدة بيانات SQLite
def init_db():
    conn = sqlite3.connect('syrx.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY, points INTEGER DEFAULT 0, last_login TEXT, wallet_address TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (user_id TEXT, task TEXT, completed BOOLEAN, PRIMARY KEY (user_id, task))''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/points/<user_id>', methods=['GET'])
def get_points(user_id):
    conn = sqlite3.connect('syrx.db')
    c = conn.cursor()
    c.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    points = result[0] if result else 0
    return jsonify({'points': points})

@app.route('/api/daily-login/<user_id>', methods=['GET', 'POST'])
def daily_login(user_id):
    conn = sqlite3.connect('syrx.db')
    c = conn.cursor()
    c.execute('SELECT last_login, points FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()

    today = str(date.today())

    if request.method == 'GET':
        can_login = not result or result[0] != today
        conn.close()
        return jsonify({'can_login': can_login})

    if request.method == 'POST':
        if not result or result[0] != today:
            new_points = (result[1] if result else 0) + 10
            c.execute('INSERT OR REPLACE INTO users (user_id, points, last_login) VALUES (?, ?, ?)',
                      (user_id, new_points, today))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'points': new_points})
        conn.close()
        return jsonify({'success': False})

@app.route('/api/task/<user_id>/<task>', methods=['POST'])
def complete_task(user_id, task):
    conn = sqlite3.connect('syrx.db')
    c = conn.cursor()
    c.execute('SELECT completed FROM tasks WHERE user_id = ? AND task = ?', (user_id, task))
    if not c.fetchone():
        c.execute('INSERT INTO tasks (user_id, task, completed) VALUES (?, ?, ?)', (user_id, task, True))
        c.execute('UPDATE users SET points = points + 5 WHERE user_id = ?', (user_id,))
        c.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
        points = c.fetchone()[0]
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'points': points})
    conn.close()
    return jsonify({'success': False})

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    conn = sqlite3.connect('syrx.db')
    c = conn.cursor()
    c.execute('SELECT user_id, points FROM users ORDER BY points DESC LIMIT 100')
    result = [{'user_id': row[0], 'points': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(result)

@app.route('/api/wallet/<user_id>', methods=['POST'])
def save_wallet(user_id):
    data = request.json
    wallet_address = data.get('wallet_address')
    if wallet_address:
        conn = sqlite3.connect('syrx.db')
        c = conn.cursor()
        c.execute('UPDATE users SET wallet_address = ? WHERE user_id = ?', (wallet_address, user_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/referral/<user_id>', methods=['POST'])
def handle_referral(user_id):
    data = request.json
    referred_user = data.get('referred_user')
    if referred_user:
        conn = sqlite3.connect('syrx.db')
        c = conn.cursor()
        c.execute('UPDATE users SET points = points + 10 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
