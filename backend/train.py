# -*- coding: utf-8 -*-
import numpy as np
import joblib
import sys
import os
from data_handler import generate_train_logs, generate_detect_logs, preprocess_data
from autoencoder_model import build_autoencoder

def train_model(log_file, model_dir):
    """
    데이터를 전처리하고, 오토인코더 모델을 학습시킨 후,
    학습된 모델과 데이터 스케일러를 파일로 저장합니다.
    """
    model_path = os.path.join(model_dir, 'anomaly_detector_model.h5')
    scaler_path = os.path.join(model_dir, 'scaler.gz')

    # 1. 데이터 전처리
    all_data, _, all_codes, scaler = preprocess_data(log_file)

    # 2. 정상 로그 데이터만 선택하여 학습에 사용
    normal_indices = [i for i, code in enumerate(all_codes) if code == 200]
    train_data = all_data[normal_indices]
    
    if len(train_data) == 0:
        print("학습할 정상 데이터가 없습니다.")
        return

    print(f"총 {len(all_data)}개의 로그 중 {len(train_data)}개의 정상 로그로 모델을 학습합니다.")

    # 3. 오토인코더 모델 생성
    input_dim = train_data.shape[1]
    autoencoder = build_autoencoder(input_dim)

    # 4. 모델 학습
    autoencoder.fit(
        train_data,
        train_data,
        epochs=50,
        batch_size=16,
        shuffle=True,
        validation_split=0.2,
        verbose=1
    )

    # 5. 학습된 모델과 스케일러 저장
    autoencoder.save(model_path)
    print(f"학습된 모델이 '{model_path}' 파일로 저장되었습니다.")
    joblib.dump(scaler, scaler_path)
    print(f"데이터 스케일러가 '{scaler_path}' 파일로 저장되었습니다.")

if __name__ == "__main__":
    # 웹 UI (main.py)를 통해 호출될 경우 (인자 2개)
    if len(sys.argv) == 3:
        log_file_path = sys.argv[1]
        model_directory = sys.argv[2]
        train_model(log_file_path, model_directory)
    # 사용자가 터미널에서 `python train.py`로 직접 실행할 경우 (인자 없음)
    elif len(sys.argv) == 1:
        print("테스트용 샘플 로그 파일을 생성하고 모델 학습을 시작합니다.")
        generate_train_logs()
        generate_detect_logs()
        print("\n--- 생성된 학습용 로그(train_access.log)로 학습을 진행합니다. ---")
        # 모델과 스케일러는 backend/models 디렉토리에 저장
        if not os.path.exists('models'):
            os.makedirs('models')
        train_model(log_file='train_access.log', model_dir='models')
    else:
        print("사용법: python train.py")
        print("또는: python train.py <로그파일_경로> <모델_디렉토리_경로>")
        sys.exit(1)

