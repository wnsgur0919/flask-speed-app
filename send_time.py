import requests

# Render로 배포된 서버 주소
url = "https://flask-speed-app.onrender.com/receive_time"

# 전송할 데이터: 사용자 이름과 도보 시간 (초 단위)
data = {
    "user": "홍길동",          # 사용자 이름
    "walk_time": 720           # 12분 (초 단위)
}

# POST 요청 전송
response = requests.post(url, json=data)

# 응답 출력
print("응답 상태코드:", response.status_code)
print("응답 내용:", response.json())
