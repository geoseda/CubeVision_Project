from shared import *
from widgets import *
from solver_worker import SolverWorker

class UiGhostcubeMixin:
    def build_net(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 14, 0, 0)

        net_card, nl = self.card("GHOSTCUBE · FLAT SIX-FACE NET")

        grid = QGridLayout()
        grid.setSpacing(12)

        self.net_labels = {}

        positions = {
            "U": (0, 1),
            "L": (1, 0),
            "F": (1, 1),
            "R": (1, 2),
            "B": (1, 3),
            "D": (2, 1)
        }

        for face, (r, c) in positions.items():
            box = QFrame()
            box.setObjectName("faceCard")

            bl = QVBoxLayout(box)
            bl.setContentsMargins(12, 8, 12, 12)
            bl.setSpacing(6)

            link = QPushButton(f"{face}  ·  {NAMES[face]}")
            link.setProperty("facelink", "true")
            link.setCursor(Qt.PointingHandCursor)
            link.setToolTip(
                f"Open the {NAMES[face]} face in the Scanner"
            )
            link.clicked.connect(
                lambda checked=False, f=face:
                self.open_face_in_scanner(f)
            )
            bl.addWidget(link)

            tiles = QGridLayout()
            tiles.setSpacing(4)

            for i in range(9):
                tile = QLabel("?")
                tile.setAlignment(Qt.AlignCenter)
                tile.setMinimumSize(34, 34)
                tile.setMaximumHeight(58)
                tile.setSizePolicy(
                    QSizePolicy.Expanding,
                    QSizePolicy.Expanding
                )

                tiles.addWidget(tile, i // 3, i % 3)
                self.net_labels[(face, i)] = tile

            bl.addLayout(tiles)
            grid.addWidget(box, r, c)

        tip = QFrame()
        tip.setObjectName("faceCard")
        tl = QVBoxLayout(tip)
        tl.setContentsMargins(16, 12, 16, 12)
        tl.addWidget(self.label("HOW TO READ", "title"))
        tl.addWidget(self.label(
            "The net unfolds the cube: Up on top, then "
            "Left · Front · Right · Back, and Down below.\n\n"
            "Click a face title to jump to it in the Scanner.",
            "hint", wrap=True
        ))
        tl.addStretch()
        grid.addWidget(tip, 0, 2, 1, 2)

        summary = QFrame()
        summary.setObjectName("faceCard")
        sl = QVBoxLayout(summary)
        sl.setContentsMargins(16, 12, 16, 12)
        sl.addWidget(self.label("CUBE STATUS", "title"))

        self.net_summary = self.label("0 / 6", "big")
        sl.addWidget(self.net_summary)
        sl.addWidget(self.label("faces scanned", "hint"))
        sl.addStretch()
        grid.addWidget(summary, 2, 2, 1, 2)

        nl.addLayout(grid, 1)
        layout.addWidget(net_card, 1)

        self.tabs.addTab(page, app_icon("ghost"), "GhostCube")
