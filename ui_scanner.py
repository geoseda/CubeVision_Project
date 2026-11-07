from shared import *
from widgets import *
from solver_worker import SolverWorker

class UiScannerMixin:
    def build_scanner(self):
        page = QWidget()
        root = QHBoxLayout(page)
        root.setContentsMargins(0, 14, 0, 0)
        root.setSpacing(16)

        # ---- left: camera -------------------------------------------
        cam_card, left = self.card("LIVE CUBE SCANNER")

        self.camera_label = QLabel("📷   Starting camera...")
        self.camera_label.setObjectName("cameraView")
        self.camera_label.setMinimumSize(520, 330)
        self.camera_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.camera_label.setAlignment(Qt.AlignCenter)
        left.addWidget(self.camera_label, 1)

        self.scan_status = self.pill(
            "Align one face inside the center 3x3 grid. "
            "Colors will fill automatically."
        )
        left.addWidget(self.scan_status)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.button(
            actions, "Capture Face", self.capture_face,
            "primary", "Freeze the detected colors  (C)", "capture"
        )
        self.button(
            actions, "Import Image", self.import_image, icon_name="import"
        )
        self.button(
            actions, "Restart Camera", self.start_camera, icon_name="restart"
        )
        self.button(
            actions, "Reset Corrections",
            self.reset_manual_corrections, "ghost",
            "Unlock manually corrected stickers"
        )

        left.addLayout(actions)

        auto_row = QHBoxLayout()
        auto_row.setSpacing(10)

        self.auto_check = ToggleSwitch(True)
        self.auto_check.setAccessibleName(
            "Automatically detect face colors"
        )
        self.auto_check.toggled.connect(
            self.toggle_auto_detection
        )
        auto_row.addWidget(self.auto_check)
        auto_row.addWidget(
            QLabel("Automatically detect face colors")
        )
        auto_row.addStretch()

        self.auto_status = QLabel("AUTO DETECTION: ON")
        self.auto_status.setProperty("badge", "on")
        auto_row.addWidget(self.auto_status)

        left.addLayout(auto_row)

        # ---- right: face editor -------------------------------------
        face_card, right = self.card("SELECT FACE")
        right.setSpacing(8)

        chips = QHBoxLayout()
        chips.setSpacing(6)

        self.face_group = QButtonGroup(self)
        self.face_group.setExclusive(True)
        self.face_buttons = {}

        for face in FACES:
            chip = QPushButton()
            chip.setCheckable(True)
            chip.setProperty("chip", "true")
            chip.setProperty("saved", "false")
            chip.setCursor(Qt.PointingHandCursor)
            chip.setToolTip(f"{NAMES[face]} face")
            chip.setAccessibleName(f"{NAMES[face]} face")
            chip.clicked.connect(
                lambda checked=False, f=face:
                self.on_chip_clicked(f)
            )

            self.face_group.addButton(chip)
            self.face_buttons[face] = chip
            chips.addWidget(chip)

        self.face_buttons["U"].setChecked(True)
        right.addLayout(chips)

        self.guide = self.label(
            "🧭  " + GUIDES["U"], "guide", wrap=True
        )
        right.addWidget(self.guide)

        grid = QGridLayout()
        grid.setSpacing(8)

        self.sticker_buttons = []

        for i in range(9):
            btn = StickerButton(i)

            btn.clicked.connect(
                lambda checked=False, index=i:
                self.change_sticker(index)
            )

            grid.addWidget(btn, i // 3, i % 3)
            self.sticker_buttons.append(btn)

        right.addLayout(grid, 1)

        right.addWidget(self.label(
            "Click a sticker to cycle its color. "
            "Corrected stickers are locked (🔒) automatically.",
            "hint", wrap=True
        ))

        self.button(
            right, "Save Selected Face", self.save_face,
            "primary", "Save this face and jump to the next  (S)", "save"
        )

        row = QHBoxLayout()
        row.setSpacing(8)

        self.button(
            row, "🔊  Read Aloud", self.read_face,
            tip="Hear the colors of this face  (V)"
        )
        self.button(
            row, "🗑  Clear Face", self.clear_face, "danger"
        )

        right.addLayout(row)

        root.addWidget(cam_card, 3)
        root.addWidget(face_card, 2)

        self.tabs.addTab(page, app_icon("capture"), "Scanner")
