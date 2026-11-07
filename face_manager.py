from shared import *
from widgets import *
from solver_worker import SolverWorker

class FaceManagerMixin:
    def refresh_stickers(self):
        for i, color in enumerate(self.edit):
            self.sticker_buttons[i].set_sticker(
                color,
                SYMBOLS[color] if color in COLORS else "?",
                i in self.manual_overrides and color in COLORS
            )

    def change_sticker(self, index):
        choices = list(COLORS)
        current = self.edit[index]

        if current in choices:
            next_index = (
                choices.index(current) + 1
            ) % len(choices)
        else:
            next_index = 0

        self.edit[index] = choices[next_index]
        self.manual_overrides.add(index)

        self.refresh_stickers()

        self.set_scan_status(
            f"Sticker {index + 1} manually corrected "
            f"to {self.edit[index]} and locked.",
            "info"
        )

    def reset_manual_corrections(self):
        self.manual_overrides.clear()
        self.scan_frozen = False
        self.auto_detect_enabled = True

        self.auto_check.setChecked(True)

        self.edit = self.live.copy()
        self.refresh_stickers()

        self.sync_auto_badge()

        self.set_scan_status(
            "Manual corrections cleared. "
            "Automatic detection resumed.",
            "ok"
        )

    def toggle_auto_detection(self, enabled):
        self.auto_detect_enabled = enabled

        if enabled:
            self.scan_frozen = False

        self.sync_auto_badge()

    def on_chip_clicked(self, face):
        if face == self.current_face:
            return

        self.face_changed(face)

    def select_face(self, face):
        self.face_buttons[face].setChecked(True)
        self.face_changed(face)

    def open_face_in_scanner(self, face):
        self.select_face(face)
        self.tabs.setCurrentIndex(TAB_SCANNER)

    def face_changed(self, face):
        if face is None:
            return

        self.current_face = face
        self.guide.setText("🧭  " + GUIDES[face])

        self.manual_overrides.clear()
        self.scan_frozen = False

        self.edit = self.faces.get(
            face,
            ["Unknown"] * 9
        ).copy()

        if face in self.faces:
            self.manual_overrides = set(range(9))

        self.refresh_stickers()
        self.sync_auto_badge()

    def save_face(self):
        face = self.current_face

        if any(
            color not in COLORS
            for color in self.edit
        ):
            QMessageBox.warning(
                self,
                "Incomplete Face",
                "Correct all unknown stickers first."
            )
            return

        self.faces[face] = self.edit.copy()

        self.manual_overrides = set(range(9))
        self.scan_frozen = True

        self.invalidate_solution()
        self.refresh_stickers()
        self.update_display()
        self.sync_auto_badge()

        self.toast.show_message(
            f"✓  {NAMES[face]} face saved  ·  "
            f"{len(self.faces)}/6",
            "ok"
        )

        self.advance_to_next_face(face)

    def advance_to_next_face(self, current):
        if len(self.faces) == 6:
            self.set_scan_status(
                "All six faces saved! Open CubeCoach to solve.",
                "ok"
            )
            self.toast.show_message(
                "🎉  All six faces saved — opening CubeCoach",
                "ok",
                3200
            )
            self.tabs.setCurrentIndex(TAB_COACH)
            return

        start = FACES.index(current)

        for step in range(1, len(FACES) + 1):
            nxt = FACES[(start + step) % len(FACES)]

            if nxt not in self.faces:
                self.select_face(nxt)

                self.set_scan_status(
                    f"{NAMES[current]} saved. "
                    f"Next up: {GUIDES[nxt]}",
                    "ok"
                )
                return

    def clear_face(self):
        face = self.current_face

        self.faces.pop(face, None)

        self.edit = ["Unknown"] * 9
        self.manual_overrides.clear()
        self.scan_frozen = False

        self.invalidate_solution()
        self.refresh_stickers()
        self.update_display()
        self.sync_auto_badge()

    def read_face(self):
        face = self.current_face

        rows = []

        for r in range(3):
            values = self.edit[
                r * 3:r * 3 + 3
            ]

            rows.append(
                f"Row {r + 1}: "
                + ", ".join(values)
            )

        message = (
            f"{NAMES[face]} face. "
            + ". ".join(rows)
        )

        self.set_scan_status(message, "info")
        self.speak(message)
