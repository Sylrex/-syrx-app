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
        """, (user_id, name, points, datetime.datetime.utcnow(), name, points, datetime.datetime.utcnow()))
        conn.commit()

        print(f"User registered/updated: {user_id}, Name: {name}, Points: {points}")
        return jsonify({"status": "success", "message": "User registered/updated successfully"})
    except Exception as e:
        conn.rollback()
        print(f"Error registering user: {str(e)}")
        return jsonify({"status": "error", "message": f"Error registering user: {str(e)}"}), 500

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
                # التحقق من عدم وجود إحالة مكررة
                cursor.execute("""
                    SELECT id FROM referrals WHERE referrer_id = %s AND referred_id = %s
                """, (referrer_id, referred_id))
                if cursor.rowcount > 0:
                    return jsonify({"status": "error", "message": "User already referred"})

                # إضافة الإحالة
                cursor.execute("""
                    INSERT INTO referrals (referrer_id, referred_id, referred_name, created_at)
                    VALUES (%s, %s, %s, %s)
                """, (referrer_id, referred_id, referred_name, datetime.datetime.utcnow()))

                # تحديث نقاط المُحيل وعدد الإحالات
                cursor.execute("""
                    UPDATE users SET points = points + 500, referrals = referrals + 1, updated_at = %s
                    WHERE user_id = %s
                """, (datetime.datetime.utcnow(), referrer_id))

                # إضافة المُحال إذا لم يكن موجودًا
                cursor.execute("""
                    INSERT INTO users (user_id, name, points, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                """, (referred_id, referred_name, points, datetime.datetime.utcnow()))

                conn.commit()

                print(f"Referral recorded: {referrer_id} -> {referred_id}")
                # استرجاع التحديثات الجديدة
                cursor.execute("SELECT referrals, points FROM users WHERE user_id = %s", (referrer_id,))
                result = cursor.fetchone()
                referral_count = result['referrals'] if result else 0
                points = result['points'] if result else 0
                return jsonify({
                    "status": "success",
                    "message": "Referral recorded",
                    "referrals": referral_count,
                    "points": points
                })
            except Exception as e:
                conn.rollback()
                print(f"Error processing referral: {str(e)}")
                return jsonify({"status": "error", "message": f"Error processing referral: {str(e)}"})
        return jsonify({"status": "error", "message": "Invalid data or same user"})
    elif request.method == 'GET':
        referrer_id = request.args.get('referrer_id')
        cursor.execute("""
            SELECT referrals, points FROM users WHERE user_id = %s
        """, (referrer_id,))
        result = cursor.fetchone()
        referral_count = result['referrals'] if result else 0
        points = result['points'] if result else 0
        return jsonify({"referrals": referral_count, "points": points})

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    cursor.execute("""
        SELECT user_id, name, points, referrals
        FROM users
        ORDER BY points DESC
        LIMIT 100
    """)
    leaderboard = [dict(row) for row in cursor.fetchall()]
    return jsonify(leaderboard)

# إغلاق الاتصال عند إغلاق التطبيق
@app.teardown_appcontext
def close_connection(exception):
    cursor.close()
    conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
