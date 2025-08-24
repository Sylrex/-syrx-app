# app.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import datetime
import psycopg
from psycopg.rows import tuple_row

# إعدادات
DB_URL = os.getenv("DATABASE_URL")  # مثال: postgresql://user:pass@host:5432/dbname
PORT = int(os.getenv("PORT", "5000"))

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

def get_conn():
    # psycopg (v3) يقرأ URL مباشرة
    return psycopg.connect(DB_URL)

def init_db():
    with get_conn() as conn:
        with conn.cursor(row_factory=tuple_row) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    points  INT DEFAULT 0,
                    last_daily_login TIMESTAMP,
                    wallet  TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id SERIAL PRIMARY KEY,
                    referrer_id BIGINT,
                    referred_id BIGINT
                )
            """)
            conn.commit()

init_db()

@app.get("/")
def serve_index():
    # يخدم index.html كصفحة التطبيق المصغر
    return send_from_directory(".", "index.html")

# نقاط المستخدم
@app.get("/api/points/<int:user_id>")
def get_points(user_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT points FROM users WHERE user_id=%s;", (user_id,))
        row = cur.fetchone()
        points = (row[0] if row else 0)
    return jsonify({"points": points})

# تسجيل دخول يومي
@app.route("/api/daily-login/<int:user_id>", methods=["GET", "POST"])
def daily_login(user_id):
    now = datetime.datetime.utcnow()
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT last_daily_login, points FROM users WHERE user_id=%s;", (user_id,))
        row = cur.fetchone()

        if request.method == "GET":
            can_login = not (row and row[0] and (now - row[0]).days < 1)
            return jsonify({"can_login": can_login})

        # POST
        if not row:
            cur.execute("INSERT INTO users (user_id, points, last_daily_login) VALUES (%s,%s,%s);",
                        (user_id, 10, now))
            points = 10
        else:
            last_login, current_points = row
            if not last_login or (now - last_login).days >= 1:
                points = (current_points or 0) + 10
                cur.execute("UPDATE users SET points=%s, last_daily_login=%s WHERE user_id=%s;",
                            (points, now, user_id))
            else:
                points = current_points or 0
        conn.commit()
    return jsonify({"success": True, "points": points})

# إكمال المهام (5 نقاط)
@app.post("/api/task/<int:user_id>/<task_name>")
def complete_task(user_id, task_name):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT points FROM users WHERE user_id=%s;", (user_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO users (user_id, points) VALUES (%s,%s);", (user_id, 5))
            points = 5
        else:
            points = (row[0] or 0) + 5
            cur.execute("UPDATE users SET points=%s WHERE user_id=%s;", (points, user_id))
        conn.commit()
    return jsonify({"success": True, "points": points})

# ربط المحفظة
@app.post("/api/wallet/<int:user_id>")
def set_wallet(user_id):
    data = request.get_json() or {}
    wallet_address = data.get("wallet_address")
    if not wallet_address:
        return jsonify({"success": False, "error": "wallet_address required"}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (user_id, wallet) VALUES (%s,%s)
            ON CONFLICT (user_id) DO UPDATE SET wallet=EXCLUDED.wallet;
        """, (user_id, wallet_address))
        conn.commit()
    return jsonify({"success": True})

# إحالة
@app.post("/api/referral/<int:user_id>")
def add_referral(user_id):
    data = request.get_json() or {}
    referred_id = data.get("referred_id")
    if not referred_id:
        return jsonify({"success": False, "error": "referred_id required"}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (%s,%s);",
                    (user_id, referred_id))
        conn.commit()
    return jsonify({"success": True})

# المتصدرون
@app.get("/api/leaderboard")
def leaderboard():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT 100;")
        data = [{"user_id": r[0], "points": r[1]} for r in cur.fetchall()]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
