
# AI 기반 웹 로그 이상 탐지 시스템

Docker와 오토인코더 딥러닝 모델을 활용하여 웹 서버의 로그를 분석하고, 실시간으로 비정상적인 접근(해킹 시도, 시스템 오류 등)을 탐지하는 시스템입니다.



---

## 주요 기능

- **AI 기반 이상 탐지**: 정상적인 로그 패턴을 학습한 오토인코더 모델을 통해 패턴에서 벗어나는 로그를 탐지합니다.
- **웹 기반 UI**: 사용자가 쉽게 로그 파일을 업로드하고, 모델 학습 및 이상 탐지를 실행할 수 있는 웹 인터페이스를 제공합니다.
- **Docker를 이용한 간편한 배포**: `docker-compose` 명령 한 번으로 프론트엔드와 백엔드 서버를 동시에 실행할 수 있습니다.
- **다양한 공격 유형 탐지**: SQL Injection, XSS, Directory Traversal 등 다양한 유형의 공격 시도 로그를 탐지할 수 있습니다.

## 동작 원리

오토인코더는 입력을 압축했다가 다시 복원하는 과정을 통해 데이터의 핵심 특징을 학습하는 비지도 학습 모델입니다. 이 프로젝트에서는 **정상적인 로그 데이터만을 학습**시켜, 정상 로그를 잘 복원해내는 모델을 만듭니다. 

만약 학습 때 보지 못한 비정상적인 로그(공격 시도)가 입력으로 들어오면, 모델은 이를 제대로 복원하지 못하고 **재구성 오류(Reconstruction Error)**가 커지게 됩니다. 이 오류가 미리 설정된 임계값(Threshold)을 초과하면 해당 로그를 '비정상'으로 판단하는 원리입니다.

## 프로젝트 구조

```
. 
├── backend/ # FastAPI 백엔드
│ ├── main.py # API 엔드포인트 정의
│ ├── data_handler.py # 로그 데이터 생성 및 전처리
│ ├── autoencoder_model.py # 오토인코더 모델 구조 정의
│ ├── train.py # 모델 학습 스크립트
│ ├── detect.py # 이상 탐지 스크립트
│ ├── requirements.txt # 백엔드 파이썬 라이브러리
│ └── Dockerfile
├── frontend/ # React 프론트엔드
│ ├── src/App.js # 메인 UI 컴포넌트
│ ├── package.json # 프론트엔드 자바스크립트 라이브러리
│ └── Dockerfile
├── docker-compose.yml # Docker 서비스 통합 실행 파일
└── .gitignore # Git 버전 관리 제외 파일 목록
```

## 설치 및 실행 방법

이 프로젝트를 실행하기 위해서는 컴퓨터에 **Docker**와 **Docker Compose**가 반드시 설치되어 있어야 합니다.

1.  **저장소 복제**
    ```bash
    git clone https://github.com/your-username/anomaly-detector.git
    cd anomaly-detector
    ```

2.  **Docker 컨테이너 빌드 및 실행**
    아래 명령어를 실행하면 필요한 모든 라이브러리를 설치하고 프론트엔드/백엔드 서버를 한 번에 실행합니다.
    ```bash
    docker-compose up --build -d
    ```

3.  **웹 애플리케이션 접속**
    웹 브라우저를 열고 `http://localhost:3000` 주소로 접속합니다.

## 사용 방법

웹 UI는 두 단계로 구성되어 있습니다.

#### 1단계: 모델 학습

1.  먼저, AI 모델을 학습시키기 위한 샘플 로그 파일을 생성해야 합니다. 아래 명령어를 터미널에서 실행하세요.
    ```bash
    docker-compose exec backend python train.py
    ```
    이 명령어는 `backend` 컨테이너 내부에서 `train.py`를 실행하여, `backend` 폴더 안에 학습용(`train_access.log`)과 탐지용(`detect_access.log`) 샘플 로그 파일을 생성합니다.

2.  웹 UI의 **'1단계: 모델 학습'** 섹션에서 **[파일 선택]** 버튼을 눌러 방금 생성된 `train_access.log` 파일을 선택합니다.
3.  **[모델 학습 시작]** 버튼을 클릭하여 학습을 진행합니다.

#### 2단계: 이상 탐지

1.  학습이 완료되면, **'2단계: 이상 탐지'** 섹션으로 이동합니다.
2.  **[파일 선택]** 버튼을 눌러 함께 생성되었던 `detect_access.log` 파일을 선택합니다.
3.  **[이상 탐지 시작]** 버튼을 클릭합니다.
4.  잠시 후, 탐지된 비정상 로그 목록이 화면에 표시됩니다.

## 기술 스택

- **Backend**: Python, FastAPI, TensorFlow/Keras, Scikit-learn
- **Frontend**: React, Bootstrap
- **Infrastructure**: Docker, Docker Compose
