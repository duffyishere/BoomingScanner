from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
)
from PySide6.QtCore import Qt, Signal, QThread

from audio.sweep_measure_worker import SweepMeasureWorker

class RecordPage(QWidget):
    next_requested = Signal(object, object, int, dict)
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.measure_duration = 7.0

        self._measurement_started = False
        self._worker_thread = None
        self._worker = None

        self._last_sweep = None
        self._last_recording = None
        self._last_fs = None
        self._last_meta = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("녹음 중...")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.status_label = QLabel(
            "테스트 신호를 재생하고, 마이크에서 신호를 수집하는 중입니다."
        )
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # 0,0 -> '계속 동글동글' 스타일
        layout.addWidget(self.progress)

        layout.addStretch()

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)

        back_button = QPushButton("뒤로 가기")
        back_button.clicked.connect(self.back_requested.emit)
        bottom_layout.addWidget(back_button)

        self.next_button = QPushButton("다음 단계로")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self._on_next_clicked)
        bottom_layout.addWidget(self.next_button)

        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def showEvent(self, event):
        super().showEvent(event)

        if not self._measurement_started:
            self._measurement_started = True
            self._start_async_measurement()

    def _start_async_measurement(self):
        self.set_status_text("테스트 스윕을 재생하면서 녹음 중입니다...")
        self.set_busy(True)

        self._worker_thread = QThread()
        self._worker = SweepMeasureWorker(
            duration=self.measure_duration
        )
        self._worker.moveToThread(self._worker_thread)

        # 스레드 → 워커.run()
        self._worker_thread.started.connect(self._worker.run)

        # 결과 처리
        self._worker.finished.connect(self._on_measurement_finished)
        self._worker.error.connect(self._on_measurement_error)

        # 정리
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)

        self._worker_thread.start()

    def _on_measurement_finished(self, sweep, recording, fs, meta):
        self._last_sweep = sweep
        self._last_recording = recording
        self._last_fs = fs
        self._last_meta = meta

        self.set_status_text("녹음이 완료되었습니다.")
        self.set_busy(False)

        if self.next_button is not None:
            self.next_button.setEnabled(True)

    def _on_next_clicked(self):
        if self._last_recording is None or self._last_fs is None:
            return

        # MainWindow에서 이 시그널을 받아 다음 페이지로 전환할 수 있도록
        # 측정 결과를 함께 전달한다.
        self.next_requested.emit(
            self._last_sweep,
            self._last_recording,
            self._last_fs,
            self._last_meta,
        )

    def _on_measurement_error(self, msg):
        self.set_status_text(f"측정 중 오류 발생: {msg}")
        self.set_busy(False)

    def set_status_text(self, text: str):
        self.status_label.setText(text)

    def set_busy(self, busy: bool):
        if busy:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 100)
            self.progress.setValue(100)

    def restart_record(self):
        self._measurement_started = False