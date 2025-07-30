# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import re

def generate_train_logs(file_path='train_access.log'):
    """
    모델 학습에 사용할 정상 로그 위주의 샘플 파일을 생성합니다.
    """
    logs = [
        '192.168.1.1 - - [22/Jul/2024:10:00:00 +0900] "GET /index.html HTTP/1.1" 200 1543',
        '192.168.1.2 - - [22/Jul/2024:10:00:01 +0900] "GET /css/style.css HTTP/1.1" 200 567',
        '192.168.1.3 - - [22/Jul/2024:10:00:02 +0900] "GET /js/main.js HTTP/1.1" 200 876',
        '192.168.1.1 - - [22/Jul/2024:10:00:03 +0900] "POST /login.php HTTP/1.1" 200 123',
        '192.168.1.4 - - [22/Jul/2024:10:01:05 +0900] "GET /products/item?id=1 HTTP/1.1" 200 980',
        '192.168.1.5 - - [22/Jul/2024:10:02:15 +0900] "GET /images/pic.jpg HTTP/1.1" 200 12345',
        '192.168.1.1 - - [22/Jul/2024:10:03:05 +0900] "GET /about.html HTTP/1.1" 200 1300',
        '192.168.1.2 - - [22/Jul/2024:10:03:10 +0900] "GET /contact.html HTTP/1.1" 200 1400',
        '192.168.1.3 - - [22/Jul/2024:10:03:15 +0900] "POST /subscribe HTTP/1.1" 200 50',
        '192.168.1.4 - - [22/Jul/2024:10:03:20 +0900] "GET /favicon.ico HTTP/1.1" 200 1500',
    ]
    with open(file_path, 'w') as f:
        for log in logs:
            f.write(log + '\n')
    print(f"학습용 샘플 로그 파일 '{file_path}'가 생성되었습니다.")

def generate_detect_logs(file_path='detect_access.log'):
    """
    이상 탐지 테스트에 사용할 로그 파일을 생성합니다.
    정상 로그와 다양한 비정상 로그를 포함합니다.
    """
    logs = [
        '192.168.1.10 - - [23/Jul/2024:11:00:00 +0900] "GET /main.js HTTP/1.1" 200 876',
        '192.168.1.11 - - [23/Jul/2024:11:00:05 +0900] "POST /login HTTP/1.1" 200 123',
        '10.0.0.1 - - [23/Jul/2024:11:01:00 +0900] "GET /admin/dashboard HTTP/1.1" 404 45',  # 비정상: 관리자 페이지 접근
        '203.0.113.45 - - [23/Jul/2024:11:02:10 +0900] "GET /search?q=<script>window.location=\'http://hacker.com\'</script>" 200 1100',  # 비정상: XSS
        '192.168.1.12 - - [23/Jul/2024:11:02:15 +0900] "GET /user/profile HTTP/1.1" 200 1500',
        '203.0.113.46 - - [23/Jul/2024:11:03:00 +0900] "GET /app/config.yml.bak HTTP/1.1" 403 150',  # 비정상: 설정 파일 백업 접근
        '203.0.113.47 - - [23/Jul/2024:11:04:00 +0900] "POST /api/v1/users HTTP/1.1" 401 88',  # 비정상: 인증 실패
        '203.0.113.48 - - [23/Jul/2024:11:05:00 +0900] "GET /?id=1%27%20UNION%20SELECT%20username,password%20FROM%20users-- HTTP/1.1" 500 210',  # 비정상: SQL Injection
        '192.168.1.13 - - [23/Jul/2024:11:05:10 +0900] "GET /products/1 HTTP/1.1" 200 1200',
        '203.0.113.49 - - [23/Jul/2024:11:06:00 +0900] "GET /../../../../etc/shadow HTTP/1.1" 403 150',  # 비정상: Directory Traversal
        '203.0.113.50 - - [23/Jul/2024:11:07:00 +0900] "GET /cgi-bin/shell.sh HTTP/1.1" 404 45',  # 비정상: 원격 코드 실행 시도
    ]
    with open(file_path, 'w') as f:
        for log in logs:
            f.write(log + '\n')
    print(f"탐지용 샘플 로그 파일 '{file_path}'가 생성되었습니다.")

def preprocess_data(log_file_path, scaler=None):
    """
    로그 파일을 읽고 전처리하여 AI 모델이 학습할 수 있는 형태로 변환합니다.

    Args:
        log_file_path (str): 처리할 로그 파일의 경로.
        scaler (MinMaxScaler, optional): 데이터 정규화에 사용할 스케일러 객체. 
                                         None이면 새로 생성하고 학습시킵니다.

    Returns:
        tuple: (정규화된 데이터, 원본 요청 로그, 학습/사용된 스케일러 객체)
    """
    # 정규표현식을 사용하여 로그의 각 부분을 파싱
    # 그룹: 1:IP, 2:Request, 3:Status Code
    log_pattern = re.compile(r'(\S+) \S+ \S+ \[.*?\] "(.*?)" (\d+)')

    parsed_logs = []
    with open(log_file_path, 'r') as f:
        for line in f:
            match = log_pattern.match(line)
            if match:
                parsed_logs.append({
                    'ip': match.group(1),
                    'request': match.group(2),
                    'code': int(match.group(3))
                })

    if not parsed_logs:
        print("파싱할 수 있는 로그가 없습니다.")
        return np.array([]), [], None

    df = pd.DataFrame(parsed_logs)

    # 1. 요청(request)의 길이
    df['request_length'] = df['request'].str.len()

    # 2. 요청 내 특수문자 개수
    df['special_chars'] = df['request'].apply(lambda x: len(re.findall(r'[^a-zA-Z0-9\s/?.=&]', x)))
    
    # AI 모델에 사용할 숫자 특징(feature)들을 선택
    features = df[['request_length', 'special_chars', 'code']]

    # 데이터 정규화 (0과 1 사이의 값으로 스케일링)
    if scaler is None:
        # train.py에서 호출될 때: 새로운 스케일러를 생성하고 학습
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(features)
    else:
        # detect.py에서 호출될 때: 기존에 학습된 스케일러를 사용
        scaled_features = scaler.transform(features)

    # 원본 요청 로그는 나중에 어떤 로그가 비정상인지 확인하기 위해 필요
    original_requests = df['request'].tolist()
    
    return scaled_features, original_requests, df['code'].tolist(), scaler
