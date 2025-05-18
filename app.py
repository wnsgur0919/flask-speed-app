from flask import Flask, request, render_template, jsonify, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'user_data.json'

# ------------------ 데이터 처리 ------------------

def load_user_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ------------------ 라우트 ------------------

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route("/set_speed", methods=["POST"])
def set_speed():
    user_name = request.form["user_name"]
    speed_type = request.form["speed_type"]
    speed_map = {"slow": 4 / 3.6, "normal": 5 / 3.6, "fast": 6 / 3.6}
    speed = round(speed_map.get(speed_type, 5 / 3.6), 2)
    data = load_user_data()
    data[user_name] = {"average_speed": speed, "history": []}
    save_user_data(data)
    return render_template("home.html", message=f"{user_name}님의 속도 설정 완료! ({speed} m/s)")

@app.route("/data")
def view_data():
    data = load_user_data()
    pretty_data = json.dumps(data, indent=4, ensure_ascii=False)
    return render_template("data.html", user_data=pretty_data)

@app.route("/edit_name", methods=["POST"])
def edit_name():
    current_name = request.form["current_name"]
    new_name = request.form["new_name"]
    data = load_user_data()
    if current_name in data:
        data[new_name] = data.pop(current_name)
        save_user_data(data)
    return redirect("/data")

@app.route("/reset_data", methods=["POST"])
def reset_data():
    save_user_data({})
    return redirect("/data")

@app.route("/api/get_speed")
def get_speed_api():
    user_name = request.args.get("user_name")
    data = load_user_data()
    user = data.get(user_name)
    if user:
        return {"speed": user.get("average_speed", 1.4)}
    return {"speed": None}

@app.route("/receive_time", methods=["POST"])
def receive_time():
    try:
        data = request.get_json()
        user = data.get("user")
        walk_time = data.get("walk_time")  # 초 단위

        if not user or walk_time is None:
            return jsonify({"status": "fail", "reason": "Invalid data"}), 400

        db = load_user_data()
        if user not in db:
            db[user] = {"average_speed": 1.4, "history": []}

        db[user]["history"].append({
            "walk_time": walk_time,
            "timestamp": datetime.now().isoformat(),
            "source": "external"
        })

        save_user_data(db)
        return jsonify({"status": "success", "message": f"{user}님의 도보 시간 저장 완료"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------ 실행 ------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
