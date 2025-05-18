from flask import Flask, render_template_string, request, redirect, jsonify
import json
import os

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
