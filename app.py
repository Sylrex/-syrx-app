from flask import Flask, send_file, render_template_string, Response, request, jsonify
import os

app = Flask(__name__)

# قاعدة بيانات مؤقتة للإحالات
referrals_db = {}
# قاعدة بيانات مؤقتة للمتصدرين
leaderboard_db = {}

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

@app.route('/referral', methods=['GET', 'POST'])
def handle_referral():
    if request.method == 'POST':
        data = request.get_json()
        referrer_id = data.get('referrer_id')
        referred_id = data.get('referred_id')
        referred_name = data.get('referred_name', 'Anonymous')
        points = data.get('points', 0)
        if referrer_id and referred_id and referrer_id != referred_id:
            if referrer_id not in referrals_db:
                referrals_db[referrer_id] = []
            if referred_id not in referrals_db[referrer_id]:
                referrals_db[referrer_id].append(referred_id)
                if referrer_id not in leaderboard_db:
                    leaderboard_db[referrer_id] = {'name': 'Anonymous', 'points': 0, 'referrals': 0}
                leaderboard_db[referrer_id]['points'] += 500
                leaderboard_db[referrer_id]['referrals'] = len(referrals_db[referrer_id])
                if referred_id not in leaderboard_db:
                    leaderboard_db[referred_id] = {'name': referred_name, 'points': points, 'referrals': 0}
                print(f"Referral recorded: {referrer_id} -> {referred_id}, Referrals: {len(referrals_db[referrer_id])}")
                return jsonify({
                    "status": "success",
                    "message": "Referral recorded",
                    "referrals": len(referrals_db[referrer_id]),
                    "points": leaderboard_db[referrer_id]['points']
                })
            return jsonify({"status": "error", "message": "User already referred"})
        return jsonify({"status": "error", "message": "Invalid data or same user"})
    elif request.method == 'GET':
        referrer_id = request.args.get('referrer_id')
        if referrer_id in referrals_db:
            return jsonify({
                "referrals": len(referrals_db[referrer_id]),
                "points": leaderboard_db.get(referrer_id, {'points': 0})['points']
            })
        return jsonify({"referrals": 0, "points": 0})

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard = [
        {
            'user_id': user_id,
            'name': data['name'],
            'points': data['points'],
            'referrals': data['referrals']
        }
        for user_id, data in leaderboard_db.items()
    ]
    leaderboard.sort(key=lambda x: x['points'], reverse=True)
    return jsonify(leaderboard[:100])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
