# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from data_handler import preprocess_data

# --- 설정값 ---
# 임계값(Threshold): 이 값보다 재구성 오류가 크면 비정상으로 판단
# 이 값은 train.py 실행 후, 학습된 모델의 정상 데이터에 대한 오류 분포를 보고 결정하는 것이 가장 좋음
# 여기서는 경험적인 값을 미리 설정
THRESHOLD = 0.1 

def detect_anomalies(log_file, model_dir):
    """
    학습된 모델과 스케일러를 불러와 새로운 로그 파일에서 이상 행위를 탐지합니다.
    """
    model_path = os.path.join(model_dir, 'anomaly_detector_model.h5')
    scaler_path = os.path.join(model_dir, 'scaler.gz')
    
    try:
        # 1. 학습된 모델과 스케일러 불러오기
        autoencoder = load_model(model_path, custom_objects={'mae': 'mae'})
        scaler = joblib.load(scaler_path)
        # print("모델과 스케일러를 성공적으로 불러왔습니다.")
    except IOError as e:
        print(f"오류: 모델 파일('{model_path}') 또는 스케일러 파일('{scaler_path}')을 찾을 수 없습니다.")
        print("먼저 'python train.py'를 실행하여 모델을 학습시켜 주세요.")
        return

    # 2. 입력받은 로그 파일 전처리
    # train.py에서 저장한 scaler 객체를 사용하여 동일한 기준으로 데이터 변환
    new_data, original_requests, _, _ = preprocess_data(log_file, scaler)
    
    if new_data.shape[0] == 0:
        print("탐지할 로그 데이터가 없습니다.")
        return

    # 3. 모델을 사용하여 데이터 재구성 및 오류 계산
    reconstructed_data = autoencoder.predict(new_data)
    # 재구성 오류: 원본 데이터와 모델이 복원한 데이터 간의 차이(MAE)
    reconstruction_error = np.mean(np.abs(new_data - reconstructed_data), axis=1)

    # 4. 이상 행위 탐지 및 결과 출력
    # print("\n--- 이상 행위 탐지 결과 ---")
    # print(f"사용한 임계값(Threshold): {THRESHOLD}")
    
    anomalies_found = 0
    for i in range(len(reconstruction_error)):
        if reconstruction_error[i] > THRESHOLD:
            anomalies_found += 1
            print(f"[!] 비정상 로그 탐지 (오류: {reconstruction_error[i]:.4f}): {original_requests[i]}")

    # if anomalies_found == 0:
    #     print("\n모든 로그가 정상 범위 내에 있습니다.")
    # else:
    #     print(f"\n총 {anomalies_found}개의 비정상(공격 의심) 로그를 탐지했습니다.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python detect.py <로그파일_경로> <모델_디렉토리_경로>")
        sys.exit(1)
    log_file = sys.argv[1]
    model_dir = sys.argv[2]
    detect_anomalies(log_file, model_dir)