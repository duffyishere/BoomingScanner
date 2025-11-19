from __future__ import annotations

from typing import Optional

import numpy as np
import sounddevice as sd
from PySide6.QtCore import QObject, Signal

from audio.sweep import generate_log_sweep

class SweepMeasureWorker(QObject):
    finished = Signal(object, object, int, dict)
    error = Signal(str)

    def __init__(
        self,
        duration: float,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self.duration = duration
        self.f_start = 20.0
        self.f_end = 1000.0
        self.fs = 48_000
        self.channels = 1

    def run(self) -> None:
        """
        QThread.started에 연결해서 실행할 엔트리 포인트.
        에러 발생 시 error 시그널을 emit 하고 종료한다.
        """
        try:
            # 1. 스윕 신호 생성
            sweep = generate_log_sweep(
                f_start=self.f_start,
                f_end=self.f_end,
                duration=self.duration,
                fs=self.fs,
            )

            # 2. 재생 + 녹음 설정 (장치는 이미 PrepPage에서 설정되었다고 가정)
            sd.default.samplerate = self.fs
            sd.default.channels = self.channels

            n_samples = sweep.shape[0]

            # playrec은 입력/출력을 동시에 처리한다.
            recording = sd.playrec(
                sweep,
                samplerate=self.fs,
                channels=self.channels,
                dtype="float32",
            )
            sd.wait()

            # 3. 메타데이터 구성
            meta = {
                "f_start": self.f_start,
                "f_end": self.f_end,
                "duration": self.duration,
                "fs": self.fs,
                "channels": self.channels,
                "n_samples": int(n_samples),
            }

            # 4. 결과 emit
            self.finished.emit(sweep, recording, self.fs, meta)

        except Exception as e:
            # UI가 표시하기 쉬운 문자열 에러 형태로 전달
            self.error.emit(str(e))