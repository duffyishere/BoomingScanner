# main.py
from ui.main_window import run_gui

def main():
    print("부밍 스캐너를 시작합니다.")

def start_measurement(mic_idx: int, spk_idx: int):
    # TODO: 나중에 실제 디바이스 이름과 sounddevice 매핑
    print(f"[INFO] 선택된 마이크: {mic_idx}")
    print(f"[INFO] 선택된 스피커: {spk_idx}")
    print("[INFO] 녹음을 시작합니다...")

    # TODO: 여기서 dsp.analyzer, booming_detector, eq 추천으로 넘기면 됨.
    print("[INFO] 측정/녹음 한 사이클 완료.")


if __name__ == "__main__":
    run_gui(on_start_measurement=start_measurement)