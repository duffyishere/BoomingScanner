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

    # 패딩(양끝 값 유지)
    pad = window_size // 2
    padded = np.pad(mag_db, (pad, pad), mode="edge")

    # 단순 이동 평균 커널
    kernel = np.ones(window_size) / window_size

    # 컨볼루션 수행
    smoothed = np.convolve(padded, kernel, mode="valid")

    return freqs, smoothed