from shared import *
from widgets import *
from solver_worker import SolverWorker

class SolverMixin:
    def invalidate_solution(self):
        self.moves = []
        self.move_index = 0

        self.render_move_empty()

        self.set_status(
            self.solver_status,
            "Save all six faces before solving.",
            "info"
        )

    def validate_cube(self):
        if len(self.faces) != 6:
            return None, "Save all six faces first."

        stickers = [
            color
            for face in FACES
            for color in self.faces[face]
        ]

        if len(stickers) != 54:
            return None, "Cube must contain 54 stickers."

        if any(
            color not in COLORS
            for color in stickers
        ):
            return None, "Invalid or unknown stickers."

        counts = Counter(stickers)

        for color in COLORS:
            if counts[color] != 9:
                return (
                    None,
                    f"{color}: {counts[color]} stickers; "
                    "expected 9."
                )

        centers = {
            face: self.faces[face][4]
            for face in FACES
        }

        if len(set(centers.values())) != 6:
            return (
                None,
                "Center colors must be unique."
            )

        expected = {
            frozenset(("White", "Yellow")),
            frozenset(("Red", "Orange")),
            frozenset(("Blue", "Green"))
        }

        actual = {
            frozenset(
                (centers[a], centers[b])
            )
            for a, b in [
                ("U", "D"),
                ("R", "L"),
                ("F", "B")
            ]
        }

        if actual != expected:
            return (
                None,
                "Opposite center colors are incorrect."
            )

        mapping = {
            color: face
            for face, color in centers.items()
        }

        facelets = "".join(
            mapping[color]
            for face in FACES
            for color in self.faces[face]
        )

        return facelets, None

    def generate_solution(self):
        facelets, error = self.validate_cube()

        if error:
            self.set_status(
                self.solver_status, error, "error"
            )
            QMessageBox.warning(
                self,
                "Invalid Cube",
                error
            )
            return

        if Cube is None:
            QMessageBox.warning(
                self,
                "Solver Missing",
                f"{SOLVER_ERROR}\n\n"
                "Install rubik-solver-py."
            )
            return

        if self.worker is not None:
            if self.worker.isRunning():
                return

        self.solve_button.setEnabled(False)

        self.set_status(
            self.solver_status,
            "⏳  Validating and solving...",
            "info"
        )

        self.worker = SolverWorker(facelets)

        self.worker.success.connect(
            self.solution_ready
        )

        self.worker.failure.connect(
            self.solution_error
        )

        self.worker.finished.connect(
            lambda: self.solve_button.setEnabled(True)
        )

        self.worker.start()

    def solution_ready(self, result):
        self.moves = (
            result.split()
            if result.strip()
            else []
        )

        self.move_index = 0

        self.rebuild_chips()

        if self.moves:
            self.set_status(
                self.solver_status,
                f"✓  Solution generated: "
                f"{len(self.moves)} moves",
                "ok"
            )
            self.toast.show_message(
                f"✨  Solution ready · {len(self.moves)} moves",
                "ok"
            )
            self.show_move()
        else:
            self.set_status(
                self.solver_status,
                "Your cube is already solved!",
                "ok"
            )
            self.render_move_empty(
                "🎉",
                "Cube already solved!",
                "ALL DONE"
            )

    def solution_error(self, error):
        self.set_status(
            self.solver_status,
            f"Solver error: {error}",
            "error"
        )

        QMessageBox.warning(
            self,
            "Solver Error",
            error
        )

    def describe_move(self, move):
        names = {
            "U": "upper",
            "R": "right",
            "F": "front",
            "D": "bottom",
            "L": "left",
            "B": "back"
        }

        face = names.get(
            move[0],
            move[0]
        )

        if move.endswith("2"):
            return (
                f"Turn {face} face 180 degrees."
            )

        if move.endswith("'"):
            return (
                f"Turn {face} face "
                "counterclockwise 90 degrees."
            )

        return (
            f"Turn {face} face "
            "clockwise 90 degrees."
        )

    def move_arrow(self, move):
        if move.endswith("2"):
            return "⟲⟳"

        if move.endswith("'"):
            return "↺"

        return "↻"

    def render_move_empty(self, big="—",
                          desc="Save all six faces, "
                               "then generate your solution.",
                          counter="NO SOLUTION YET"):
        self.move_big.setText(big)
        self.move_desc.setText(desc)
        self.move_counter.setText(counter)

        self.move_progress.setRange(0, 1)
        self.move_progress.setValue(0)

        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.speak_button.setEnabled(False)
        self.copy_button.setEnabled(False)

        self.clear_chips()

    def clear_chips(self):
        self.move_chips = []

        while self.chip_grid.count():
            item = self.chip_grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        placeholder = self.label(
            "Your move list will appear here.", "hint"
        )
        self.chip_grid.addWidget(placeholder, 0, 0)

    def rebuild_chips(self):
        self.clear_chips()

        # remove the placeholder that clear_chips just added
        while self.chip_grid.count():
            item = self.chip_grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        columns = 12

        for i, move in enumerate(self.moves):
            chip = QPushButton(move)
            chip.setCursor(Qt.PointingHandCursor)
            chip.setToolTip(self.describe_move(move))
            chip.setProperty("movechip", "todo")
            chip.clicked.connect(
                lambda checked=False, idx=i:
                self.jump_to_move(idx)
            )

            self.chip_grid.addWidget(
                chip, i // columns, i % columns
            )
            self.move_chips.append(chip)

    def jump_to_move(self, index):
        if 0 <= index < len(self.moves):
            self.move_index = index
            self.show_move()

    def show_move(self):
        if not self.moves:
            return

        total = len(self.moves)
        move = self.moves[self.move_index]

        self.move_counter.setText(
            f"MOVE {self.move_index + 1} OF {total}"
        )

        self.move_progress.setRange(0, total)
        self.move_progress.setValue(self.move_index + 1)

        self.move_big.setText(move)

        self.move_desc.setText(
            f"{self.move_arrow(move)}   "
            f"{self.describe_move(move)}"
        )

        for i, chip in enumerate(self.move_chips):
            if i < self.move_index:
                state = "done"
            elif i == self.move_index:
                state = "current"
            else:
                state = "todo"

            chip.setProperty("movechip", state)
            repolish(chip)

        self.prev_button.setEnabled(self.move_index > 0)
        self.next_button.setEnabled(True)
        self.speak_button.setEnabled(True)
        self.copy_button.setEnabled(True)

    def next_move(self):
        if not self.moves:
            return

        if self.move_index < len(self.moves) - 1:
            self.move_index += 1
            self.show_move()
        else:
            self.toast.show_message(
                "🎉  That was the last move — "
                "your cube should be solved!",
                "ok",
                3600
            )

    def previous_move(self):
        if not self.moves:
            return

        self.move_index = max(
            0,
            self.move_index - 1
        )

        self.show_move()

    def speak_move(self):
        if not self.moves:
            return

        move = self.moves[self.move_index]

        self.speak(
            self.describe_move(move)
        )

    def copy_solution(self):
        if not self.moves:
            return

        QApplication.clipboard().setText(
            " ".join(self.moves)
        )

        self.toast.show_message(
            "📋  Solution copied to clipboard"
        )

    def rescue_mode(self):
        answer = QMessageBox.question(
            self,
            "Cube Rescue",
            "Clear all scans and rescan the cube?",
            QMessageBox.Yes | QMessageBox.No
        )

        if answer == QMessageBox.Yes:
            self.reset_cube()
            self.tabs.setCurrentIndex(TAB_SCANNER)
