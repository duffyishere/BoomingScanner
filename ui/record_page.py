from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
)
from PySide6.QtCore import Qt, Signal


class RecordPage(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
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

        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def set_status_text(self, text: str):
        self.status_label.setText(text)

    def set_busy(self, busy: bool):
        if busy:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 100)
            self.progress.setValue(100)