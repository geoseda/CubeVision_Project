from shared import *
from widgets import *
from solver_worker import SolverWorker

class UiCoachMixin:
    def build_coach(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 14, 0, 0)
        layout.setSpacing(16)

        top, tl = self.card("CUBECOACH · SMART SOLVER")

        row = QHBoxLayout()
        row.setSpacing(12)

        self.solver_status = self.pill(
            "Save all six faces before solving."
        )
        row.addWidget(self.solver_status, 1)

        self.solve_button = QPushButton(
            "✨  Validate Cube & Generate Solution"
        )
        self.solve_button.setProperty("variant", "primary")
        self.solve_button.setCursor(Qt.PointingHandCursor)
        self.solve_button.clicked.connect(self.generate_solution)
        row.addWidget(self.solve_button)

        tl.addLayout(row)
        layout.addWidget(top)

        # big move card
        move_card = QFrame()
        move_card.setObjectName("moveCard")

        ml = QVBoxLayout(move_card)
        ml.setContentsMargins(24, 18, 24, 18)
        ml.setSpacing(6)

        self.move_counter = self.label(
            "NO SOLUTION YET", "title", align=Qt.AlignCenter
        )
        ml.addWidget(self.move_counter)

        self.move_progress = QProgressBar()
        self.move_progress.setTextVisible(False)
        self.move_progress.setFixedHeight(8)
        self.move_progress.setRange(0, 1)
        self.move_progress.setValue(0)
        ml.addWidget(self.move_progress)

        self.move_big = self.label(
            "—", name="bigMove", align=Qt.AlignCenter
        )
        ml.addWidget(self.move_big, 1)

        self.move_desc = self.label(
            "Save all six faces, then generate your solution.",
            name="moveDesc", wrap=True, align=Qt.AlignCenter
        )
        ml.addWidget(self.move_desc)

        nav = QHBoxLayout()
        nav.setSpacing(10)

        self.prev_button = self.button(
            nav, "◀  Previous", self.previous_move,
            tip="Previous move  (P)"
        )
        self.speak_button = self.button(
            nav, "🔊  Speak Move", self.speak_move,
            tip="Hear this move  (M)"
        )
        self.next_button = self.button(
            nav, "Next  ▶", self.next_move, "primary",
            "Next move  (N)"
        )

        ml.addLayout(nav)
        layout.addWidget(move_card, 1)

        # chips
        chips_card, cl = self.card("FULL SOLUTION")

        self.chip_grid = QGridLayout()
        self.chip_grid.setSpacing(6)
        cl.addLayout(self.chip_grid)

        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        self.copy_button = self.button(
            bottom, "📋  Copy Solution", self.copy_solution
        )
        bottom.addStretch()
        self.button(
            bottom, "🛟  Cube Rescue - Rescan Cube",
            self.rescue_mode, "danger"
        )

        cl.addLayout(bottom)
        layout.addWidget(chips_card)

        self.move_chips = []
        self.render_move_empty()

        self.tabs.addTab(page, app_icon("coach"), "CubeCoach")
