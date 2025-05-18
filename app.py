from flask import Flask, render_template_string, request, redirect
import json
import os

app = Flask(__name__)
DATA_FILE = 'user_data.json'

# ------------------ 데이터 처리 ------------------
def load_user_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_user_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ------------------ 템플릿: 사용자 설정 ------------------
setup_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>사용자 설정</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; text-align: center; }
        input, button { padding: 10px; margin: 10px; font-size: 16px; width: 80%; }
    </style>
</head>
<body>
    <h1>사용자 이름과 평균 속도 설정</h1>
    <form method="POST" action="/set_speed">
        사용자 이름: <input type="text" name="user_name" required><br>
        <button type="submit" name="speed_type" value="slow">느림 (4km/h)</button>
        <button type="submit" name="speed_type" value="normal">보통 (5km/h)</button>
        <button type="submit" name="speed_type" value="fast">빠름 (6km/h)</button>
    </form>
    {% if message %}
        <p style="color:green;"><strong>{{ message }}</strong></p>
    {% endif %}
    <p>
        <a href="/map">[지도 보기]</a> |
        <a href="/data">[데이터 보기]</a>
    </p>
</body>
</html>
"""

# ------------------ 템플릿: 데이터 보기 ------------------
data_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>사용자 데이터</title>
    <style>
        body { font-family: Arial; padding: 20px; max-width: 800px; margin: auto; }
        textarea { width: 100%; height: 300px; font-family: monospace; font-size: 14px; }
        form { margin-top: 20px; }
    </style>
</head>
<body>
    <h1>사용자 데이터</h1>
    <textarea readonly>{{ user_data }}</textarea>
    <form method="POST" action="/edit_name">
        현재 이름: <input type="text" name="current_name" required>
        → 수정 이름: <input type="text" name="new_name" required>
        <button type="submit">수정</button>
    </form>
    <form method="POST" action="/reset_data" onsubmit="return confirm('정말 모든 데이터를 초기화할까요?');">
        <button type="submit" style="margin-top:10px;color:red;">모든 데이터 초기화</button>
    </form>
    <p><a href="/">[홈으로]</a> | <a href="/map">[지도 보기]</a></p>
</body>
</html>
"""

# ------------------ 템플릿: 지도 ------------------
map_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>경로 예측 지도</title>
    <style>
        body { font-family: Arial; padding: 20px; max-width: 800px; margin: auto; }
        input { padding: 8px; margin: 5px; width: 45%; }
        button { padding: 10px 20px; margin-top: 10px; font-size: 16px; }
        #map { width: 100%; height: 400px; margin-top: 20px; }
    </style>
    <script src="https://dapi.kakao.com/v2/maps/sdk.js?appkey=702531c2283a267c0f3d762a745ff1ee&autoload=true&libraries=services,geometry"></script>
</head>
<body>
    <div style="margin-bottom: 20px;">
        <form action="/" method="get" style="display:inline;"><button>홈</button></form>
        <form action="/data" method="get" style="display:inline;"><button>데이터 보기</button></form>
    </div>
    <h1>출발지와 목적지를 입력하세요</h1>
    <form id="routeForm">
        <input type="text" id="start" placeholder="출발지 (예: 서울역)" required>
        <input type="text" id="end" placeholder="도착지 (예: 경복궁)" required><br>
        <input type="text" id="user_name" placeholder="사용자 이름" required><br>
        <button type="submit">경로 예측</button>
    </form>
    <div id="map"></div>
<script>
const mapContainer = document.getElementById('map');
const map = new kakao.maps.Map(mapContainer, {
    center: new kakao.maps.LatLng(37.5665, 126.9780),
    level: 5
});
const places = new kakao.maps.services.Places();
let marker = null;

document.getElementById('routeForm').onsubmit = function(e) {
    e.preventDefault();
    const start = document.getElementById("start").value.trim();
    const end = document.getElementById("end").value.trim();
    const user_name = document.getElementById("user_name").value.trim();
    if (!start || !end || !user_name) {
        alert("모든 필드를 입력해주세요.");
        return;
    }
    places.keywordSearch(start, function(startResult, status1) {
        if (status1 !== kakao.maps.services.Status.OK || !startResult.length) {
            alert("출발지를 찾을 수 없습니다.");
            return;
        }
        places.keywordSearch(end, function(endResult, status2) {
            if (status2 !== kakao.maps.services.Status.OK || !endResult.length) {
                alert("도착지를 찾을 수 없습니다.");
                return;
            }
            const startCoords = new kakao.maps.LatLng(startResult[0].y, startResult[0].x);
            const endCoords = new kakao.maps.LatLng(endResult[0].y, endResult[0].x);
            const distance = kakao.maps.geometry.spherical.computeDistance(startCoords, endCoords);
            if (marker) marker.setMap(null);
            marker = new kakao.maps.Marker({ map: map, position: endCoords });
            map.panTo(endCoords);
            fetch(`/api/get_speed?user_name=${encodeURIComponent(user_name)}`)
                .then(res => res.json())
                .then(data => {
                    if (!data.speed) {
                        alert("사용자 속도가 설정되어 있지 않습니다.");
                        return;
                    }
                    const speed = data.speed;
                    const estimated = distance / speed;
                    const minutes = Math.round(estimated / 60);
                    const km = (distance / 1000).toFixed(2);
                    alert(`총 거리: ${km}km\n예상 소요 시간: 약 ${minutes}분`);
                });
        });
    });
};
</script>
</body>
</html>
"""

# ------------------ 라우팅 ------------------

@app.route("/")
def index():
    return render_template_string(setup_template)

@app.route("/map")
def map_page():
    return render_template_string(map_template)

@app.route("/set_speed", methods=["POST"])
def set_speed():
    user_name = request.form["user_name"]
    speed_type = request.form["speed_type"]
    speed_map = {"slow": 4 / 3.6, "normal": 5 / 3.6, "fast": 6 / 3.6}
    speed = round(speed_map.get(speed_type, 5 / 3.6), 2)
    data = load_user_data()
    data[user_name] = {"average_speed": speed, "history": []}
    save_user_data(data)
    return render_template_string(setup_template, message=f"{user_name}님의 속도 설정 완료! ({speed} m/s)")

@app.route("/data")
def view_data():
    data = load_user_data()
    pretty_data = json.dumps(data, indent=4, ensure_ascii=False)
    return render_template_string(data_template, user_data=pretty_data)

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

# ------------------ 실행 ------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
