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

class MainWindow(QWidget):
    def __init__(self, on_start_measurement=None):
        super().__init__()
        self.on_start_measurement = on_start_measurement

        self.setWindowTitle("BoomingScanner")
        self.setMinimumSize(600, 500)

        self._build_ui()

    def _build_ui(self):
        self.stack = QStackedWidget()

        self.prep_page = PrepPage()
        self.record_page = RecordPage()
        
        self.stack.addWidget(self.prep_page)   # index 0
        self.stack.addWidget(self.record_page)  # index 1

        self.prep_page.start_requested.connect(self._on_start_requested)
        self.record_page.back_requested.connect(self._on_back_from_record)

        root_layout = QVBoxLayout()
        root_layout.addWidget(self.stack)
        self.setLayout(root_layout)

    def _on_start_requested(self, selected_mic: str, selected_speaker: str):
        """
        준비 페이지에서 '측정 시작' 눌렀을 때:
        1) 녹음 페이지로 전환
        2) 외부(on_start_measurement) 콜백 호출
        """
        print(f"[UI] start_requested: mic={selected_mic}, speaker={selected_speaker}")

        self.stack.setCurrentWidget(self.record_page)

        if self.on_start_measurement is not None:
            self.on_start_measurement(selected_mic, selected_speaker)

    def _on_back_from_record(self):
        print("[UI] back_requested from RecordPage")
        self.stack.setCurrentWidget(self.prep_page)

def run_gui(on_start_measurement=None):
    app = QApplication(sys.argv)
    window = MainWindow(on_start_measurement=on_start_measurement)
    window.show()
    sys.exit(app.exec())