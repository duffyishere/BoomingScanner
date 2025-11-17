from __future__ import annotations

import sounddevice as sd
from typing import List, Dict, Any


DeviceInfo = Dict[str, Any]


def _query_all_devices() -> List[DeviceInfo]:
    return sd.query_devices()


def get_input_devices() -> List[DeviceInfo]:
    """
    입력(마이크) 장치 목록을 반환한다.

    각 요소는 다음 키를 가진 dict:
    - index: PortAudio 디바이스 인덱스 (int)
    - name: 장치 이름 (str)
    - max_input_channels: 사용 가능한 입력 채널 수 (int)
    - default_samplerate: 기본 샘플레이트 (float)
    """
    devices = _query_all_devices()
    inputs: List[DeviceInfo] = []

    for idx, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0:
            inputs.append(
                {
                    "index": idx,
                    "name": dev.get("name", f"Device {idx}"),
                    "max_input_channels": dev.get("max_input_channels", 0),
                    "default_samplerate": dev.get("default_samplerate", 0.0),
                }
            )

    return inputs


def get_output_devices() -> List[DeviceInfo]:
    """
    출력(스피커/헤드폰) 장치 목록을 반환한다.

    각 요소는 다음 키를 가진 dict:
    - index: PortAudio 디바이스 인덱스 (int)
    - name: 장치 이름 (str)
    - max_output_channels: 사용 가능한 출력 채널 수 (int)
    - default_samplerate: 기본 샘플레이트 (float)
    """
    devices = _query_all_devices()
    outputs: List[DeviceInfo] = []

    for idx, dev in enumerate(devices):
        if dev.get("max_output_channels", 0) > 0:
            outputs.append(
                {
                    "index": idx,
                    "name": dev.get("name", f"Device {idx}"),
                    "max_output_channels": dev.get("max_output_channels", 0),
                    "default_samplerate": dev.get("default_samplerate", 0.0),
                }
            )

    return outputs


def set_default_devices(input_index: int | None = None, output_index: int | None = None) -> None:
    """
    기본 입력/출력 장치를 설정한다.

    Args:
        input_index: sounddevice 장치 인덱스 (입력용)
        output_index: sounddevice 장치 인덱스 (출력용)
    """
    current = sd.default.device

    in_dev = input_index if input_index is not None else current[0]
    out_dev = output_index if output_index is not None else current[1]

    sd.default.device = (in_dev, out_dev)
    print(f"[INFO] 기본 장치 설정됨: 입력={in_dev}, 출력={out_dev}")

if __name__ == "__main__":
    print("=== 입력 장치 목록 ===")
    for d in get_input_devices():
        print(
            f"[{d['index']}] {d['name']} "
            f"(입력 채널: {d['max_input_channels']}, {d['default_samplerate']} Hz)"
        )

    print("\n=== 출력 장치 목록 ===")
    for d in get_output_devices():
        print(
            f"[{d['index']}] {d['name']} "
            f"(출력 채널: {d['max_output_channels']}, {d['default_samplerate']} Hz)"
        )