from shared import *
from widgets import *
from solver_worker import SolverWorker

class UiAccessibilityMixin:
    def build_accessibility(self):
        page = QWidget()
        root = QHBoxLayout(page)
        root.setContentsMargins(0, 14, 0, 0)
        root.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(16)

        # display mode
        mode_card, ml = self.card("DISPLAY MODE")

        ml.addWidget(self.label(
            "Choose how sticker colors are shown on the camera "
            "overlay, the GhostCube net and the scanner.",
            "hint", wrap=True
        ))

        grid = QGridLayout()
        grid.setSpacing(8)

        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_buttons = {}

        for i, (name, (icon, _)) in enumerate(MODE_INFO.items()):
            btn = QPushButton(f"{icon}   {name}")
            btn.setCheckable(True)
            btn.setProperty("chip", "true")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(
                lambda checked=False, n=name:
                self.change_mode(n)
            )

            self.mode_group.addButton(btn)
            self.mode_buttons[name] = btn
            grid.addWidget(btn, i // 2, i % 2)

        self.mode_buttons[self.mode].setChecked(True)
        ml.addLayout(grid)

        self.mode_hint = self.pill(MODE_INFO[self.mode][1])
        ml.addWidget(self.mode_hint)

        left.addWidget(mode_card)

        # voice
        voice_card, vl = self.card("VOICE ASSISTANCE")

        row = QHBoxLayout()
        row.setSpacing(10)

        self.voice_switch = ToggleSwitch(True)
        self.voice_switch.setAccessibleName(
            "Enable voice assistance"
        )
        self.voice_switch.toggled.connect(
            lambda value: setattr(
                self, "voice_enabled", value
            )
        )

        row.addWidget(self.voice_switch)
        row.addWidget(QLabel("Enable voice assistance"))
        row.addStretch()

        vl.addLayout(row)

        self.rate_label = self.label(
            f"Speech speed: {self.voice_rate} words / min",
            "hint"
        )
        vl.addWidget(self.rate_label)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(100, 250)
        slider.setValue(self.voice_rate)
        slider.setAccessibleName("Speech speed")
        slider.valueChanged.connect(self.change_rate)
        vl.addWidget(slider)

        self.button(
            vl, "▶  Test Voice",
            lambda: self.speak("Welcome to CubeVision X"),
            "primary"
        )

        left.addWidget(voice_card)
        left.addStretch()

        # legend
        legend_card, ll = self.card("COLOR LEGEND")

        ll.addWidget(self.label(
            "Every color has its own symbol and pattern, "
            "so the cube can be read without relying on color.",
            "hint", wrap=True
        ))

        grid = QGridLayout()
        grid.setSpacing(12)

        for i, (name, rgb) in enumerate(COLORS.items()):
            rgb = tuple(int(v) for v in rgb)

            tile = QLabel(
                "<div style='font-size:30px;'>"
                f"{html.escape(str(SYMBOLS[name]))}</div>"
                "<div style='font-size:15px;'>"
                f"<b>{html.escape(name)}</b></div>"
                "<div style='font-size:13px;'>"
                f"{html.escape(PATTERNS[name])}</div>"
            )
            tile.setAlignment(Qt.AlignCenter)
            tile.setMinimumHeight(110)
            tile.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Expanding
            )
            tile.setStyleSheet(
                f"background: rgb{rgb};"
                f"color: {ideal_text(rgb)};"
                "border-radius: 16px;"
                "border: 1px solid rgba(255,255,255,0.25);"
            )
            grid.addWidget(tile, i // 3, i % 3)

        ll.addLayout(grid, 1)

        root.addLayout(left, 2)
        root.addWidget(legend_card, 3)

        self.tabs.addTab(page, app_icon("accessibility"), "Accessibility")
