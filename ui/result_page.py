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

from dsp.analyzer import process_frequency_response, detect_booming_bands

class ResultPage(QWidget):
    back_requested = Signal()

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
        self.back_button.clicked.connect(self.back_requested.emit)

        bottom_layout.addWidget(self.back_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def set_measurement_data(self, sweep, recording, fs, meta):
        freqs, mag_db_norm, baseline = process_frequency_response(
            recording,
            fs,
            f_min=meta.get("f_start", 20.0),
            f_max=meta.get("f_end", 1000.0),
            window_size=24,
            baseline_method="median",
        )
        if freqs is None:
            self.summary_label.setText("측정 신호가 너무 짧아서 분석할 수 없습니다.")
            self.booming_text.clear()
            self.eq_text.clear()
            return

        # 1) 부밍 대역 탐지
        booming_bands = detect_booming_bands(
            freqs,
            mag_db_norm,
        )

        # 2) 그래프 갱신 (부밍 대역 하이라이트 포함)
        self.plot_frequency_response(freqs, mag_db_norm, booming_bands=booming_bands)

        # 3) 부밍 텍스트 영역 업데이트
        if booming_bands:
            lines = []
            for band in booming_bands:
                lines.append(
                    f"{band['f_start']:.1f}–{band['f_end']:.1f} Hz"
                    f" (피크 {band['peak_freq']:.1f} Hz, +{band['peak_gain_db']:.1f} dB)"
                )
            self.booming_text.setPlainText("\n".join(lines))
        else:
            self.booming_text.setPlainText("유의미한 부밍 대역이 감지되지 않았습니다.")

        # 4) 간단한 EQ 추천 생성
        eq_lines = []
        for i, band in enumerate(booming_bands, start=1):
            peak_freq = band["peak_freq"]
            peak_gain = band["peak_gain_db"]

            bandwidth = max(band["f_end"] - band["f_start"], 1.0)
            Q = peak_freq / (bandwidth * 2.0)
            Q = max(0.3, min(Q, 10.0))

            gain_cut = -min(peak_gain, 8.0)  # 너무 과하지 않게 최대 -8dB까지

            eq_lines.append(
                f"Filter {i}: Peaking, {peak_freq:.1f} Hz, {gain_cut:.1f} dB, Q={Q:.1f}"
            )

        if eq_lines:
            self.eq_text.setPlainText("\n".join(eq_lines))
        else:
            self.eq_text.setPlainText("EQ 조정이 꼭 필요해 보이지는 않습니다.")

        # 5) 요약 레이블 업데이트
        if booming_bands:
            worst = max(booming_bands, key=lambda b: b["peak_gain_db"])
            self.summary_label.setText(
                f"가장 강한 부밍은 약 {worst['peak_freq']:.1f} Hz 근처에서 "
                f"+{worst['peak_gain_db']:.1f} dB 정도로 감지되었습니다.\n"
                "제안된 EQ 설정을 참고해 저역을 조정해 보세요."
            )
        else:
            self.summary_label.setText(
                "저역 대역에서 특별히 튀는 공명은 감지되지 않았습니다.\n"
                "현재 스피커/방 세팅은 비교적 균형 잡힌 상태입니다."
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
        self.ax.plot([0, 1000], [0, 0], color="black", linewidth=0.8, linestyle=":")

        self.figure.tight_layout()
        self.canvas.draw()