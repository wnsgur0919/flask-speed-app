import requests

url = "https://flask-speed-app.onrender.com/receive_time"

data = {
    "user": "홍길동",
    "walk_time": 680  # 예: 11분 20초
}

response = requests.post(url, json=data)

print("응답 코드:", response.status_code)
print("응답 내용:", response.json())
