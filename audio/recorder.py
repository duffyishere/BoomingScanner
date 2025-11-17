import sounddevice as sd
import numpy as np


def record_mic(
    duration: float = 3.0,
    fs: int = 48_000,
    channels: int = 1,
) -> np.ndarray:
    """
    현재 기본 입력 장치(default input device)를 사용하여
    일정 시간 동안 오디오를 녹음합니다.

    Args:
        duration: 녹음 시간(초)
        fs: 샘플레이트(Hz)
        channels: 입력 채널 수

    Returns:
        녹음된 오디오 데이터를 담고 있는 NumPy 배열
        shape: (샘플 수, 채널 수)
    """
    print(f"[INFO] 기본 입력 장치로 {duration}초 동안 녹음합니다...")

    sd.default.samplerate = fs
    sd.default.channels = channels

    num_samples = int(duration * fs)
    recording = sd.rec(num_samples, dtype="float32")
    sd.wait()

    print("[INFO] 녹음 완료")
    print(f"       shape={recording.shape}, samplerate={fs}Hz, channels={channels}")
    return recording


if __name__ == "__main__":
    # 로컬 테스트용
    audio = record_mic(duration=2.0)
    print("[DEBUG] 로컬 테스트 완료, shape:", audio.shape)