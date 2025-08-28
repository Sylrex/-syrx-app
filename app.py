from flask import Flask, send_file, render_template_string, Response, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

app = Flask(__name__)

# الاتصال بقاعدة البيانات PostgreSQL
db_url = os.environ.get('DATABASE_URL')
try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # إنشاء الجداول تلقائيًا عند بدء التطبيق
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL DEFAULT 'Anonymous',
            points INTEGER NOT NULL DEFAULT 0,
            referrals INTEGER NOT NULL DEFAULT 0,
            daily_tries INTEGER NOT NULL DEFAULT 5,
            last_login TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id SERIAL PRIMARY KEY,
            referrer_id VARCHAR(255) REFERENCES users(user_id),
            referred_id VARCHAR(255) REFERENCES users(user_id),
            referred_name VARCHAR(255) NOT NULL DEFAULT 'Anonymous',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(referrer_id, referred_id)
        );
    """)
    conn.commit()
    print("Database tables created or verified successfully")
except Exception as e:
    print(f"Error initializing database: {str(e)}")
    raise

@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            return render_template_string(file.read())
    except FileNotFoundError:
        return Response("Error: index.html not found", status=404)

@app.route('/SYRXApp')
def redirect_syrxapp():
    return Response("Redirecting to homepage", status=302, headers={"Location": "/"})

@app.route('/tonconnect-manifest.json')
def serve_manifest():
    try:
        return send_file('tonconnect-manifest.json')
    except FileNotFoundError:
        return Response("Error: tonconnect-manifest.json not found", status=404)

@app.route('/<path:filename>')
def serve_static(filename):
    try:
        if os.path.exists(filename):
            return send_file(filename)
        else:
            return Response(f"Error: {filename} not found", status=404)
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)

@app.route('/user', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        name = data.get('name', 'Anonymous')
        points = data.get('points', 0)

        if not user_id:
            return jsonify({"status": "error", "message": "user_id is required"}), 400

        # تحديث أو إضافة المستخدم في جدول users
        cursor.execute("""
            INSERT INTO users (user_id, name, points, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET name = %s, points = %s, updated_at = %s
        """, (user_id, name, points, datetime.datetime.utcnow(),
              name, points, datetime.datetime.utcnow()))
        conn.commit()

        print(f"User registered/updated: {user_id}, Name: {name}, Points: {points}")
        return jsonify({"status": "success", "message": "User registered/updated successfully"})
    except Exception as e:
        conn.rollback()
        print(f"Error registering user: {str(e)}")
        return jsonify({"status": "error", "message": f"Error registering user: {str(e)}"}), 500

@app.route('/daily-login', methods=['POST'])
def daily_login():
    """تسجيل دخول يومي، يمنح المستخدم 5 محاولات يوميًا إذا مرت 24 ساعة"""
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400

    cursor.execute("SELECT daily_tries, last_login FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    now = datetime.datetime.utcnow()

    if not user:
        # إنشاء مستخدم جديد
        cursor.execute("""
            INSERT INTO users (user_id, daily_tries, last_login)
            VALUES (%s, %s, %s)
        """, (user_id, 5, now))
        conn.commit()
        return jsonify({"status": "success", "daily_tries": 5, "message": "User created and daily tries set to 5"})

    last_login = user['last_login']
    daily_tries = user['daily_tries']

    if not last_login or (now - last_login).total_seconds() >= 24*3600:
        # إعادة التجديد اليومي
        daily_tries = 5
        cursor.execute("UPDATE users SET daily_tries = %s, last_login = %s WHERE user_id = %s",
                       (daily_tries, now, user_id))
        conn.commit()
        return jsonify({"status": "success", "daily_tries": daily_tries, "message": "Daily tries reset to 5"})

    if daily_tries <= 0:
        return jsonify({"status": "error", "daily_tries": 0, "message": "No daily tries left, wait 24 hours"})

    # تقليل محاولة واحدة
    daily_tries -= 1
    cursor.execute("UPDATE users SET daily_tries = %s WHERE user_id = %s", (daily_tries, user_id))
    conn.commit()
    return jsonify({"status": "success", "daily_tries": daily_tries, "message": "Daily try used, remaining tries updated"})

@app.route('/referral', methods=['GET', 'POST'])
def handle_referral():
    if request.method == 'POST':
        data = request.get_json()
        referrer_id = data.get('referrer_id')
        referred_id = data.get('referred_id')
        referred_name = data.get('referred_name', 'Anonymous')
        points = data.get('points', 0)

        if referrer_id and referred_id and referrer_id != referred_id:
            try:
                cursor.execute("SELECT id FROM referrals WHERE referrer_id = %s AND referred_id = %s", (referrer_id, referred_id))
                if cursor.rowcount > 0:
                    return jsonify({"status": "error", "message": "User already referred"})

                cursor.execute("INSERT INTO referrals (referrer_id, referred_id, referred_name, created_at) VALUES (%s,%s,%s,%s)",
                               (referrer_id, referred_id, referred_name, datetime.datetime.utcnow()))

                cursor.execute("UPDATE users SET points = points + 500, referrals = referrals + 1, updated_at = %s WHERE user_id = %s",
                               (datetime.datetime.utcnow(), referrer_id))

                cursor.execute("INSERT INTO users (user_id, name, points, updated_at) VALUES (%s,%s,%s,%s) ON CONFLICT (user_id) DO NOTHING",
                               (referred_id, referred_name, points, datetime.datetime.utcnow()))

                conn.commit()

                cursor.execute("SELECT referrals, points FROM users WHERE user_id = %s", (referrer_id,))
                result = cursor.fetchone()
                return jsonify({
                    "status": "success",
                    "message": "Referral recorded",
                    "referrals": result['referrals'] if result else 0,
                    "points": result['points'] if result else 0
                })
            except Exception as e:
                conn.rollback()
                return jsonify({"status": "error", "message": f"Error processing referral: {str(e)}"})
        return jsonify({"status": "error", "message": "Invalid data or same user"})
    elif request.method == 'GET':
        referrer_id = request.args.get('referrer_id')
        cursor.execute("SELECT referrals, points FROM users WHERE user_id = %s", (referrer_id,))
        result = cursor.fetchone()
        return jsonify({"referrals": result['referrals'] if result else 0, "points": result['points'] if result else 0})

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    cursor.execute("SELECT user_id, name, points, referrals FROM users ORDER BY points DESC LIMIT 100")
    leaderboard = [dict(row) for row in cursor.fetchall()]
    return jsonify(leaderboard)

@app.teardown_appcontext
def close_connection(exception):
    cursor.close()
    conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
