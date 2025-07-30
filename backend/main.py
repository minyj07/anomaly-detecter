

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import subprocess

app = FastAPI()

# CORS 설정 (React 앱과 통신하기 위함)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 React 앱의 주소만 허용하는 것이 안전합니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/app/uploaded_files"
MODEL_DIR = "/app/models"

@app.on_event("startup")
def on_startup():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Anomaly Detector Backend!"}

@app.post("/train/")
async def train_model(file: UploadFile = File(...)):
    log_file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(log_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 기존 train.py 스크립트를 실행합니다.
    # Docker 컨테이너 내에서 실행되도록 경로를 수정해야 할 수 있습니다.
    process = subprocess.run(
        ["python", "train.py", log_file_path, MODEL_DIR],
        capture_output=True,
        text=True
    )

    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Model training failed: {process.stderr}")

    return JSONResponse(content={"message": "Model trained successfully.", "output": process.stdout})

@app.post("/detect/")
async def detect_anomalies(file: UploadFile = File(...)):
    log_file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(log_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 기존 detect.py 스크립트를 실행합니다.
    process = subprocess.run(
        ["python", "detect.py", log_file_path, MODEL_DIR],
        capture_output=True,
        text=True
    )

    # --- 디버깅 코드 추가 ---
    print("--- detect.py STDOUT ---")
    print(process.stdout)
    print("--- detect.py STDERR ---")
    print(process.stderr)
    print("------------------------")
    # --- 디버깅 코드 끝 ---

    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Detection failed: {process.stderr}")

    # detect.py의 출력을 파싱하여 JSON으로 반환
    anomalies = []
    if process.stdout:
        for line in process.stdout.strip().split('\n'):
            if line.startswith("[!"):
                anomalies.append(line)
    
    print(f"Found anomalies: {anomalies}")

    return JSONResponse(content={"anomalies": anomalies})

