from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QFormLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal

class PrepPage(QWidget):
    # (selected_mic: str, selected_speaker: str)를 넘겨줌
    start_requested = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        # 1. 디바이스 설정 영역
        device_group = QGroupBox("입출력 장치 설정")
        device_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        device_layout = QFormLayout()

        self.mic_combo = QComboBox()
        self.speaker_combo = QComboBox()
        # TODO: 나중에 실제 디바이스 리스트로 채우기
        self.mic_combo.addItems(["기본 마이크 (시스템 설정)", "USB Mic 1", "USB Mic 2"])
        self.speaker_combo.addItems(["기본 스피커 (시스템 설정)", "스튜디오 모니터 L/R", "헤드폰 출력"])

        device_layout.addRow("마이크 입력 장치", self.mic_combo)
        device_layout.addRow("스피커 출력 장치", self.speaker_combo)

        device_group.setLayout(device_layout)
        root_layout.addWidget(device_group)
        root_layout.addSpacing(16)

        # 2. 안내 텍스트 영역
        guide_group = QGroupBox("측정 전 안내")
        guide_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        guide_layout = QVBoxLayout()

        guide_text = (
            "스윕 녹음을 시작하기 전에 아래 사항을 확인해주세요.\n\n"
            "1. 마이크는 기본 입력 장치로 설정하고, 노이즈 억제/AGC를 끕니다.\n"
            "2. 스피커는 EQ/음장 효과 없이 원음으로 출력되도록 설정합니다.\n"
            "3. 마이크는 실제 청취 위치의 귀 높이에 배치합니다.\n"
            "4. 주변 소음을 최대한 줄이고, 측정 중에는 움직이지 않습니다.\n"
        )

        guide_label = QLabel(guide_text)
        guide_label.setWordWrap(True)

        guide_layout.addWidget(guide_label)
        guide_group.setLayout(guide_layout)
        root_layout.addWidget(guide_group)
        root_layout.addSpacing(16)

        # 3. 체크리스트 영역
        checklist_group = QGroupBox("체크리스트")
        checklist_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        checklist_layout = QVBoxLayout()

        self.chk_mic = QCheckBox("마이크 입력 장치를 올바르게 선택했습니다.")
        self.chk_noise = QCheckBox("노이즈 억제 / 자동 이득 조절(AGC)을 껐습니다.")
        self.chk_speaker = QCheckBox("스피커 EQ/음장 효과를 모두 껐습니다.")
        self.chk_position = QCheckBox("마이크를 청취 위치의 귀 높이에 정확히 배치했습니다.")
        self.chk_env = QCheckBox("주변 소음을 최대한 줄였습니다.")

        for chk in [
            self.chk_mic,
            self.chk_noise,
            self.chk_speaker,
            self.chk_position,
            self.chk_env,
        ]:
            checklist_layout.addWidget(chk)

        checklist_group.setLayout(checklist_layout)
        root_layout.addWidget(checklist_group)

        # 4 경고 라벨 영역
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #c0392b;")
        self.warning_label.setWordWrap(True)
        root_layout.addWidget(self.warning_label)

        root_layout.addSpacing(16)

        # 5. 하단 버튼 영역
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)

        self.start_button = QPushButton("측정 시작")
        self.start_button.clicked.connect(self._on_start_clicked)

        bottom_layout.addWidget(self.start_button)
        root_layout.addLayout(bottom_layout)

        self.setLayout(root_layout)

    def _on_start_clicked(self):
        unchecked = [
            chk.text()
            for chk in [
                self.chk_mic,
                self.chk_noise,
                self.chk_speaker,
                self.chk_position,
                self.chk_env,
            ]
            if not chk.isChecked()
        ]

        if unchecked:
            print("[WARN] 체크 안 된 항목이 있습니다:")
            for item in unchecked:
                print(" -", item)
            warning_lines = "\n".join(f"• {item}" for item in unchecked)
            self.warning_label.setText(
                "체크되지 않은 항목이 있습니다. 아래 항목을 확인해주세요.\n" + warning_lines
            )
            return
        self.warning_label.clear()

        selected_mic = self.mic_combo.currentText()
        selected_speaker = self.speaker_combo.currentText()

        self.start_requested.emit(selected_mic, selected_speaker)