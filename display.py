from shared import *
from widgets import *
from solver_worker import SolverWorker

class DisplayMixin:
    def tile_text(self, color):
        if color not in COLORS:
            return "?", 14

        if self.mode == "Symbols":
            return str(SYMBOLS[color]), 15

        if self.mode == "Patterns":
            return PATTERNS[color], 11

        if self.mode == "Color Names":
            return color, 9

        return "", 12

    def update_display(self):
        for face in FACES:
            stickers = self.faces.get(
                face,
                ["Unknown"] * 9
            )

            tiles = self.progress_cards[face]["tiles"]

            for i, color in enumerate(stickers):
                label = self.net_labels[(face, i)]
                text, size = self.tile_text(color)

                label.setText(text)
                label.setToolTip(
                    f"{NAMES[face]} #{i + 1}: "
                    f"{color if color in COLORS else 'not scanned'}"
                )

                if color in COLORS:
                    rgb = rgb_of(color)
                    fg = ideal_text(rgb)
                    bg = f"rgb{rgb}"
                else:
                    fg = "#94A3B8"
                    bg = "rgba(71, 85, 105, 0.55)"
                    rgb = None

                border = (
                    "2px solid rgba(255,255,255,0.75)"
                    if i == 4
                    else "1px solid rgba(255,255,255,0.12)"
                )

                label.setStyleSheet(
                    f"background: {bg};"
                    f"color: {fg};"
                    f"border: {border};"
                    "border-radius: 8px;"
                    "font-weight: 700;"
                    f"font-size: {size}px;"
                )

                tiles[i].setStyleSheet(
                    f"background: {bg};"
                    "border-radius: 6px;"
                )

            saved = face in self.faces

            status = self.progress_cards[face]["status"]
            status.setText("✓ SAVED" if saved else "NOT SAVED")
            status.setProperty(
                "badge", "on" if saved else "pending"
            )
            repolish(status)

            chip = self.face_buttons[face]
            chip.setText(
                f"{face}\n{'✓ ' if saved else ''}{NAMES[face]}"
            )
            chip.setProperty(
                "saved", "true" if saved else "false"
            )
            repolish(chip)

        count = len(self.faces)

        self.progress_label.setText(
            f"{count} / 6 faces scanned"
        )
        self.progress_bar.setValue(count)
        self.header_progress.setValue(count)
        self.header_label.setText(
            f"FACES SAVED  {count} / 6"
        )
        self.net_summary.setText(f"{count} / 6")
