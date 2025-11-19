from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
)
from PySide6.QtCore import Qt
import sys

from ui.prep_page import PrepPage
from ui.record_page import RecordPage
from ui.result_page import ResultPage

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BoomingScanner")
        self.setMinimumSize(600, 600)

        self._build_ui()

    def _build_ui(self):
        self.stack = QStackedWidget()

        self.prep_page = PrepPage()
        self.record_page = RecordPage()
        self.result_page = ResultPage()
        
        self.stack.addWidget(self.prep_page)   # index 0
        self.stack.addWidget(self.record_page)  # index 1
        self.stack.addWidget(self.result_page)  # index 2

        self.prep_page.next_requested.connect(self._on_start_requested)

        self.record_page.next_requested.connect(self._on_record_next)
        self.record_page.back_requested.connect(self._on_back_from_record)

        root_layout = QVBoxLayout()
        root_layout.addWidget(self.stack)
        self.setLayout(root_layout)

    def _on_start_requested(self, mic_idx: int, spk_idx: int):
        """
        준비 페이지에서 '측정 시작' 눌렀을 때:
        1) 녹음 페이지로 전환
        2) 비동기방식 측정/녹음 시작
        """
        print(f"[UI] start_requested: mic idx={mic_idx}, speaker idx={spk_idx}")

        self.stack.setCurrentWidget(self.record_page)

    def _on_record_next(self, sweep, recording, fs, meta):
        self.result_page.set_measurement_data(
            sweep=sweep,
            recording=recording,
            fs=fs,
            meta=meta,
        )
        self.stack.setCurrentWidget(self.result_page)

    def _on_back_from_record(self):
        print("[UI] back_requested from RecordPage")
        self.record_page.restart_record()
        self.stack.setCurrentWidget(self.prep_page)

def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())