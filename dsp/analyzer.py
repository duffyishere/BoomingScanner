import numpy as np

def compute_frequency_response(recording, fs):
    """
    녹음된 신호로부터 주파수 응답을 계산한다.

    Args:
        recording: 1채널 녹음 데이터 (numpy 배열 또는 리스트)
        fs: 샘플레이트 (예: 48000)

    Returns:
        freqs: 주파수 배열 (Hz)
        mag_db: 각 주파수에 대한 크기(dB)
    """
    x = np.asarray(recording).astype(float).squeeze()

    if x.ndim != 1 or x.size < 8:
        return None, None

    window = np.hanning(x.size)
    x_win = x * window

    fft = np.fft.rfft(x_win)

    mag = np.abs(fft)
    mag[mag == 0] = 1e-12 

    mag_db = 20.0 * np.log10(mag)

    freqs = np.fft.rfftfreq(x_win.size, d=1.0 / fs)

    mask = (freqs >= 20.0) & (freqs <= 500.0)
    freqs_band = freqs[mask]
    mag_db_band = mag_db[mask]

    return freqs_band, mag_db_band


# 이동 평균 기반의 스무딩 함수 추가
def smooth_response(freqs, mag_db, window_size: int = 7):
    """
    이동 평균(Moving Average)방식으로 스무딩을 수행한다.

    Args:
        freqs: 주파수 배열
        mag_db: dB 값 배열
        window_size: 스무딩에 사용할 윈도우 크기(홀수 권장)

    Returns:
        freqs: 기존 주파수 배열
        smoothed: 스무딩된 dB 배열
    """
    if freqs is None or mag_db is None:
        return None, None

    if window_size < 1:
        return freqs, mag_db

    pad = window_size // 2
    padded = np.pad(mag_db, (pad, pad), mode="edge")

    kernel = np.ones(window_size) / window_size

    smoothed = np.convolve(padded, kernel, mode="valid")

    return freqs, smoothed

def normalize_response(freqs, mag_db, method: str = "median"):
    """
    주파수 응답에서 기준선(baseline)을 추정하고 0dB 기준으로 정규화한다.

    - 전체 응답의 중앙값(또는 평균값)을 기준선으로 사용하고,
      각 주파수의 dB 값에서 이를 빼서 '상대적인 튐'만 남긴다.
    - 이렇게 하면 전체 그래프 기울기나 절대 음압 레벨보다는
      '어디가 얼마나 튀었는지'를 보기 쉬워진다.

    Args:
        freqs: 주파수 배열
        mag_db: dB 값 배열
        method: 'median' 또는 'mean' (baseline 산출 방식)

    Returns:
        freqs: 원래 주파수 배열
        normalized: baseline을 0dB로 맞춘 정규화된 dB 배열
        baseline: 기준선으로 사용된 값(dB)
    """
    if freqs is None or mag_db is None:
        return None, None, None

    if method == "mean":
        baseline = float(np.mean(mag_db))
    else:
        baseline = float(np.median(mag_db))

    normalized = mag_db - baseline
    return freqs, normalized, baseline

def process_frequency_response(
    recording,
    fs,
    f_min: float = 20.0,
    f_max: float = 500.0,
    window_size: int = 7,
    baseline_method: str = "median",
):
    """
    FFT -> 대역 슬라이싱 -> 스무딩 -> 기준선 정규화를 한 번에 수행하는 헬퍼 함수.

    Args:
        recording: 1채널 녹음 데이터
        fs: 샘플레이트
        f_min: 사용할 최소 주파수(Hz)
        f_max: 사용할 최대 주파수(Hz)
        window_size: 스무딩 윈도우 크기
        baseline_method: 'median' 또는 'mean'

    Returns:
        freqs: 주파수 배열 (f_min~f_max 구간)
        mag_db_norm: baseline을 0dB로 정규화한 dB 배열
        baseline: 기준선 값(dB)
    """
    freqs, mag_db = compute_frequency_response(recording, fs)
    if freqs is None or mag_db is None:
        return None, None, None

    freqs_s, mag_db_smooth = smooth_response(freqs, mag_db, window_size=window_size)
    freqs_n, mag_db_norm, baseline = normalize_response(
        freqs_s,
        mag_db_smooth,
        method=baseline_method,
    )
    return freqs_n, mag_db_norm, baseline


def detect_booming_bands(
    freqs,
    mag_db_norm,
    threshold_db: float = 6.0,
    min_bandwidth_hz: float = 5.0,
):
    """
    정규화된 주파수 응답에서 부밍(과도한 피크) 대역을 탐지한다.

    - baseline(0dB) 대비 threshold_db 이상 튀어 오른 구간을 부밍 후보로 본다.
    - 연속된 구간을 하나의 대역으로 묶고, 각 대역의 피크 주파수/크기를 계산한다.

    Args:
        freqs: 주파수 배열 (Hz)
        mag_db_norm: baseline을 0dB로 정규화한 dB 배열
        threshold_db: 이 값 이상 튀어오른 구간을 부밍으로 판단
        min_bandwidth_hz: 이 값보다 좁은 대역은 노이즈로 간주하고 무시

    Returns:
        booming_bands: 다음 형태의 dict 리스트
            [
                {
                    "f_start": float,
                    "f_end": float,
                    "peak_freq": float,
                    "peak_gain_db": float,
                },
                ...
            ]
    """
    if freqs is None or mag_db_norm is None:
        return []

    freqs = np.asarray(freqs)
    mag_db_norm = np.asarray(mag_db_norm)

    if freqs.size == 0 or mag_db_norm.size == 0:
        return []

    over = mag_db_norm >= threshold_db

    bands = []
    in_band = False
    start_idx = 0

    for i, is_over in enumerate(over):
        if is_over and not in_band:
            in_band = True
            start_idx = i
        elif not is_over and in_band:
            end_idx = i - 1
            f_start = float(freqs[start_idx])
            f_end = float(freqs[end_idx])

            if f_end - f_start >= min_bandwidth_hz:
                segment = mag_db_norm[start_idx : end_idx + 1]
                peak_rel_idx = int(np.argmax(segment))
                peak_idx = start_idx + peak_rel_idx
                bands.append(
                    {
                        "f_start": f_start,
                        "f_end": f_end,
                        "peak_freq": float(freqs[peak_idx]),
                        "peak_gain_db": float(mag_db_norm[peak_idx]),
                    }
                )
            in_band = False

    if in_band:
        end_idx = len(over) - 1
        f_start = float(freqs[start_idx])
        f_end = float(freqs[end_idx])
        if f_end - f_start >= min_bandwidth_hz:
            segment = mag_db_norm[start_idx : end_idx + 1]
            peak_rel_idx = int(np.argmax(segment))
            peak_idx = start_idx + peak_rel_idx
            bands.append(
                {
                    "f_start": f_start,
                    "f_end": f_end,
                    "peak_freq": float(freqs[peak_idx]),
                    "peak_gain_db": float(mag_db_norm[peak_idx]),
                }
            )

    return bands