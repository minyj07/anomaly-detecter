# -*- coding: utf-8 -*-
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

def build_autoencoder(input_dim):
    """
    오토인코더 모델의 구조를 정의하고 컴파일합니다.

    Args:
        input_dim (int): 입력 데이터의 특징(feature) 개수.

    Returns:
        tensorflow.keras.Model: 컴파일된 오토인코더 모델.
    """
    # --- 인코더 (Encoder) ---
    # 입력층
    input_layer = Input(shape=(input_dim,), name="INPUT")
    
    # 인코딩을 통해 입력 데이터를 점차 저차원으로 압축
    # input_dim -> 16 -> 8 -> 4 (잠재 공간, Latent Space)
    encoded = Dense(16, activation='relu', name="ENCODE_1")(input_layer)
    encoded = Dense(8, activation='relu', name="ENCODE_2")(encoded)
    latent_vector = Dense(4, activation='relu', name="LATENT_VECTOR")(encoded)

    # --- 디코더 (Decoder) ---
    # 잠재 공간의 벡터를 다시 원본 차원으로 복원
    # 4 -> 8 -> 16 -> input_dim (출력층)
    decoded = Dense(8, activation='relu', name="DECODE_1")(latent_vector)
    decoded = Dense(16, activation='relu', name="DECODE_2")(decoded)
    output_layer = Dense(input_dim, activation='sigmoid', name="OUTPUT")(decoded)

    # 오토인코더 모델 정의
    autoencoder = Model(input_layer, output_layer)

    # 모델 컴파일
    # optimizer: 모델을 어떻게 업데이트할지 결정 (adam은 일반적으로 성능이 좋음)
    # loss: 모델의 예측이 실제와 얼마나 다른지를 측정 (mae: Mean Absolute Error)
    autoencoder.compile(optimizer='adam', loss='mae')
    
    # 모델 구조 요약 출력
    autoencoder.summary()
    
    return autoencoder
