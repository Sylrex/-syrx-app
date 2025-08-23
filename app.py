from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import datetime

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT', 5432)

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            points INT DEFAULT 0,
            last_daily_login TIMESTAMP,
            wallet TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id SERIAL PRIMARY KEY,
            referrer_id BIGINT,
            referred_id BIGINT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# نقاط المستخدم
@app.route('/api/points/<int:user_id>', methods=['GET'])
def get_points(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT points FROM users WHERE user_id=%s;", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    points = result[0] if result else 0
    return jsonify({'points': points})

# تسجيل دخول يومي
@app.route('/api/daily-login/<int:user_id>', methods=['GET','POST'])
def daily_login(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT last_daily_login, points FROM users WHERE user_id=%s;", (user_id,))
    result = cur.fetchone()
    now = datetime.datetime.utcnow()

    if request.method == 'GET':
        can_login = not (result and result[0] and (now - result[0]).days < 1)
        cur.close()
        conn.close()
        return jsonify({'can_login': can_login})

    points = 10
    if not result:
        cur.execute("INSERT INTO users (user_id, points, last_daily_login) VALUES (%s,%s,%s);",
                    (user_id, points, now))
    else:
        last_login, current_points = result
        if not last_login or (now - last_login).days >= 1:
            points = current_points + 10
            cur.execute("UPDATE users SET points=%s, last_daily_login=%s WHERE user_id=%s;",
                        (points, now, user_id))
        else:
            points = current_points

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True, 'points': points})

# إكمال المهام
@app.route('/api/task/<int:user_id>/<task_name>', methods=['POST'])
def complete_task(user_id, task_name):
    conn = get_db_connection()
    cur = conn.cursor()
    task_points = 5
    cur.execute("SELECT points FROM users WHERE user_id=%s;", (user_id,))
    result = cur.fetchone()
    if not result:
        cur.execute("INSERT INTO users (user_id, points) VALUES (%s,%s);", (user_id, task_points))
        points = task_points
    else:
        points = result[0] + task_points
        cur.execute("UPDATE users SET points=%s WHERE user_id=%s;", (points, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True, 'points': points})

# ربط المحفظة
@app.route('/api/wallet/<int:user_id>', methods=['POST'])
def set_wallet(user_id):
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, wallet) VALUES (%s,%s) ON CONFLICT(user_id) DO UPDATE SET wallet=%s;",
                (user_id, wallet_address, wallet_address))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True})

# الإحالات
@app.route('/api/referral/<int:user_id>', methods=['POST'])
def add_referral(user_id):
    data = request.get_json() or {}
    referred_id = data.get('referred_id')
    if not referred_id:
        return jsonify({'success': False, 'error':'No referred_id'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO referrals (referrer_id,referred_id) VALUES (%s,%s);", (user_id, referred_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True})

# لوحة المتصدرين
@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT 100;")
    result = cur.fetchall()
    cur.close()
    conn.close()
    leaderboard = [{'user_id': r[0], 'points': r[1]} for r in result]
    return jsonify(leaderboard)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)))
