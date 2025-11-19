from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QGroupBox,
)
from PySide6.QtCore import Qt, Signal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from dsp.analyzer import compute_frequency_response, smooth_response

class ResultPage(QWidget):
    back_to_start_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("측정 결과")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        graph_group = QGroupBox("주파수 응답 그래프")
        graph_layout = QVBoxLayout()

        # 1. Matplotlib 그래프 캔버스
        self.figure = Figure(figsize=(7, 4.5))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        graph_layout.addWidget(self.canvas)
        graph_group.setLayout(graph_layout)
        layout.addWidget(graph_group)

        # 2. 부밍 대역 / 문제 구간 영역
        booming_group = QGroupBox("감지된 부밍 / 문제 대역")
        booming_layout = QVBoxLayout()

        self.booming_text = QPlainTextEdit()
        self.booming_text.setReadOnly(True)
        self.booming_text.setPlaceholderText("예) 60–80Hz: +7dB (부밍 의심)\n")
        booming_layout.addWidget(self.booming_text)

        booming_group.setLayout(booming_layout)
        layout.addWidget(booming_group)

        # 3. EQ 추천 영역
        eq_group = QGroupBox("EQ 추천")
        eq_layout = QVBoxLayout()

        self.eq_text = QPlainTextEdit()
        self.eq_text.setReadOnly(True)
        self.eq_text.setPlaceholderText(
            "예)\n"
            "Filter 1: Peaking, 70Hz, -4.0dB, Q=4.0\n"
            "Filter 2: Peaking, 45Hz, -3.0dB, Q=2.5\n"
        )
        eq_layout.addWidget(self.eq_text)

        eq_group.setLayout(eq_layout)
        layout.addWidget(eq_group)

        # 4. 요약 영역
        summary_group = QGroupBox("요약")
        summary_layout = QVBoxLayout()

        self.summary_label = QLabel(
            "아직 분석 결과가 없습니다.\n녹음을 완료하면 이곳에 전체 요약이 표시됩니다."
        )
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        layout.addStretch()

        # 하단 버튼 영역
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)

        self.back_button = QPushButton("처음으로 돌아가기")
        self.back_button.clicked.connect(self.back_to_start_requested.emit)

        bottom_layout.addWidget(self.back_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def set_measurement_data(self, sweep, recording, fs, meta):
        freqs, mag_db = compute_frequency_response(recording, fs)
        if freqs is None:
            self.summary_label.setText("측정 신호가 너무 짧아서 분석할 수 없습니다.")
            return
        freqs, mag_db_smooth = smooth_response(freqs, mag_db, window_size=7)

        self.plot_frequency_response(freqs, mag_db_smooth)        

        self.summary_label.setText(
            "기본 주파수 응답을 계산하여 그래프로 표시했습니다.\n"
            "다음 단계에서 부밍 구간을 탐지하는 로직을 추가할 수 있습니다."
        )
    
    def plot_frequency_response(self, freqs, response_db, booming_bands=None):
        """
        freqs: 주파수 배열(Hz)
        response_db: 각 주파수에 대한 dB 값 배열
        booming_bands: 선택 사항. [{'f_start': .., 'f_end': ..}, ...] 형태의 리스트.
        """
        if freqs is None or response_db is None:
            return

        self.ax.clear()

        # 기본 응답 곡선
        self.ax.plot(freqs, response_db, linewidth=1.2)

        # 부밍 대역 하이라이트
        if booming_bands:
            for band in booming_bands:
                f_start = band.get("f_start")
                f_end = band.get("f_end")
                if f_start is not None and f_end is not None:
                    self.ax.axvspan(f_start, f_end, color="red", alpha=0.15)

        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Magnitude (dB)")
        self.ax.set_title("Frequency Response")
        self.ax.grid(True, which="both", linestyle="--", alpha=0.3)
        self.ax.plot([20, 500], [0, 0], color="black", linewidth=0.8, linestyle=":")

        self.figure.tight_layout()
        self.canvas.draw()