from shared import *
from widgets import *
from solver_worker import SolverWorker

class UiProgressMixin:
    def build_progress(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 14, 0, 0)
        layout.setSpacing(16)

        top, tl = self.card("SCAN PROGRESS")

        self.progress_label = self.label("0 / 6 faces scanned", "big")
        tl.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        tl.addWidget(self.progress_bar)

        layout.addWidget(top)

        grid = QGridLayout()
        grid.setSpacing(14)

        self.progress_cards = {}

        for n, face in enumerate(FACES):
            box = QFrame()
            box.setObjectName("card")

            bl = QHBoxLayout(box)
            bl.setContentsMargins(18, 14, 18, 14)
            bl.setSpacing(16)

            info = QVBoxLayout()
            info.setSpacing(6)

            info.addWidget(self.label(
                f"{face} · {NAMES[face]}", "big"
            ))

            status = QLabel("NOT SAVED")
            status.setProperty("badge", "pending")
            status.setAlignment(Qt.AlignCenter)
            info.addWidget(status)

            rescan = QPushButton("Open in Scanner")
            rescan.setProperty("variant", "ghost")
            rescan.setCursor(Qt.PointingHandCursor)
            rescan.clicked.connect(
                lambda checked=False, f=face:
                self.open_face_in_scanner(f)
            )
            info.addWidget(rescan)
            info.addStretch()

            bl.addLayout(info, 1)

            mini = QGridLayout()
            mini.setSpacing(3)

            tiles = []

            for i in range(9):
                tile = QLabel()
                tile.setFixedSize(26, 26)
                mini.addWidget(tile, i // 3, i % 3)
                tiles.append(tile)

            bl.addLayout(mini)

            self.progress_cards[face] = {
                "status": status,
                "tiles": tiles
            }

            grid.addWidget(box, n // 3, n % 3)

        layout.addLayout(grid, 1)

        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.button(
            actions, "📤  Export JSON", self.export_json, "primary"
        )
        self.button(
            actions, "↺  Reset Cube", self.confirm_reset, "danger"
        )

        layout.addLayout(actions)

        self.tabs.addTab(page, app_icon("progress"), "Progress")
