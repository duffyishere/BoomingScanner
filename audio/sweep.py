import numpy as np

def generate_log_sweep(
    f_start: float = 20.0,
    f_end: float = 500.0,
    duration: float = 5.0,
    fs: int = 48_000,
) -> np.ndarray:
    if f_start <= 0 or f_end <= 0:
        raise ValueError("f_start와 f_end는 0보다 커야 합니다.")
    if f_end <= f_start:
        raise ValueError("f_end는 f_start보다 커야 합니다.")

    n_samples = int(duration * fs)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    k = np.log(f_end / f_start) / duration
    phase = 2 * np.pi * f_start * (np.exp(k * t) - 1) / k
    sweep = np.sin(phase)

    fade_len = int(0.01 * fs)
    if fade_len > 0:
        window = np.ones_like(sweep)
        fade_in = np.linspace(0.0, 1.0, fade_len)
        fade_out = np.linspace(1.0, 0.0, fade_len)
        window[:fade_len] = fade_in
        window[-fade_len:] = fade_out
        sweep *= window

    return sweep.astype(np.float32)


if __name__ == "__main__":
    import sounddevice as sd

    sweep = generate_log_sweep(20, 500, duration=10.0, fs=48_000)
    sd.play(sweep, samplerate=48_000)
    sd.wait()