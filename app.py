from flask import Flask, send_file, render_template_string, Response, request, jsonify
from flask_cors import CORS
import os
import urllib.parse as urlparse
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # تحسين CORS للسماح لكل الأصول

# إعداد Connection Pool
db_pool = None
try:
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise Exception("DATABASE_URL not found in environment")
    
    url = urlparse.urlparse(db_url)
    
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        dbname=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
        sslmode='require'  # ضروري مع Render
    )
    print("Database pool initialized successfully")
except Exception as e:
    print(f"Error initializing database pool: {e}")

@contextmanager
def get_db_connection():
    if not db_pool:
        raise Exception("Database pool not initialized")
    conn = None
    try:
        conn = db_pool.getconn()
        yield conn
    finally:
        if conn:
            db_pool.putconn(conn)

# تنفيذ init_db.sql عند بدء التطبيق
def init_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if os.path.exists('init_db.sql'):
                    with open('init_db.sql', 'r') as file:
                        sql_commands = file.read().split(';')
                        for cmd in sql_commands:
                            if cmd.strip():
                                cur.execute(cmd)
                    conn.commit()
                    print("Database initialized successfully with init_db.sql")
                else:
                    print("init_db.sql not found, skipping database initialization")
    except Exception as e:
        print(f"Error initializing database: {e}")

init_db()

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
def update_user():
    data = request.get_json()
    user_id = data.get('user_id')
    name = data.get('name', 'Anonymous')
    points = data.get('points', 0)
    if not user_id:
        return jsonify({"status": "error", "message": "Invalid user_id"})
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (user_id, name, points, referrals)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id)
                    DO UPDATE SET name = EXCLUDED.name, points = EXCLUDED.points
                    RETURNING points, referrals;
                """, (user_id, name, points, 0))
                result = cur.fetchone()
                conn.commit()
                print(f"User updated: {user_id}, Points: {points}, Name: {name}, Referrals: {result[1]}")
                return jsonify({
                    "status": "success",
                    "message": "User updated",
                    "points": result[0],
                    "referrals": result[1]
                })
    except Exception as e:
        print(f"Error updating user: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/user', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Invalid user_id"})
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT points, referrals, name
                    FROM users
                    WHERE user_id = %s;
                """, (user_id,))
                result = cur.fetchone()
                if result:
                    return jsonify({
                        "status": "success",
                        "points": result[0],
                        "referrals": result[1],
                        "name": result[2]
                    })
                return jsonify({"status": "error", "message": "User not found"})
    except Exception as e:
        print(f"Error fetching user: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/referral', methods=['GET', 'POST'])
def handle_referral():
    if request.method == 'POST':
        data = request.get_json()
        referrer_id = data.get('referrer_id')
        referred_id = data.get('referred_id')
        referred_name = data.get('referred_name', 'Anonymous')
        if not (referrer_id and referred_id and referrer_id != referred_id):
            return jsonify({"status": "error", "message": "Invalid data or same user"})
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (user_id, name, points, referrals)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (user_id) DO NOTHING;
                    """, (referred_id, referred_name, 0, 0))
                    cur.execute("""
                        INSERT INTO referrals (referrer_id, referred_id)
                        VALUES (%s, %s)
                        ON CONFLICT (referrer_id, referred_id) DO NOTHING
                        RETURNING id;
                    """, (referrer_id, referred_id))
                    result = cur.fetchone()
                    if result:
                        cur.execute("""
                            UPDATE users
                            SET points = points + 500,
                                referrals = referrals + 1
                            WHERE user_id = %s
                            RETURNING points, referrals;
                        """, (referrer_id,))
                        updated = cur.fetchone()
                        conn.commit()
                        print(f"Referral recorded: {referrer_id} -> {referred_id}, Referrals: {updated[1]}, Points: {updated[0]}")
                        return jsonify({
                            "status": "success",
                            "message": "Referral recorded",
                            "referrals": updated[1],
                            "points": updated[0]
                        })
                    return jsonify({"status": "error", "message": "User already referred"})
        except Exception as e:
            print(f"Error processing referral: {e}")
            return jsonify({"status": "error", "message": str(e)})
    elif request.method == 'GET':
        referrer_id = request.args.get('referrer_id')
        if not referrer_id:
            return jsonify({"referrals": 0, "points": 0})
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT points, referrals
                        FROM users
                        WHERE user_id = %s;
                    """, (referrer_id,))
                    result = cur.fetchone()
                    if result:
                        return jsonify({"referrals": result[1], "points": result[0]})
                    return jsonify({"referrals": 0, "points": 0})
        except Exception as e:
            print(f"Error fetching referrals: {e}")
            return jsonify({"status": "error", "message": str(e)})

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT user_id, name, points, referrals
                    FROM users
                    ORDER BY points DESC, referrals DESC
                    LIMIT 100;
                """)
                leaderboard = [
                    {
                        'user_id': row[0],
                        'name': row[1],
                        'points': row[2],
                        'referrals': row[3]
                    }
                    for row in cur.fetchall()
                ]
                print(f"Leaderboard fetched: {len(leaderboard)} users")
                response = jsonify(leaderboard)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                return response
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
