from shared import *
from widgets import *
from solver_worker import SolverWorker

class ProjectDataMixin:
    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Cube Data",
            "cubevision.json",
            "JSON (*.json)"
        )

        if not path:
            return

        data = {
            "project": "CubeVision X",
            "faces": self.faces,
            "solution": self.moves,
            "display_mode": self.mode
        }

        try:
            Path(path).write_text(
                json.dumps(data, indent=2),
                encoding="utf-8"
            )

            self.toast.show_message(
                f"📤  Exported: {Path(path).name}",
                "ok"
            )

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Export Error",
                str(exc)
            )

    def confirm_reset(self):
        answer = QMessageBox.question(
            self,
            "Reset Cube",
            "Clear all saved faces and the current solution?",
            QMessageBox.Yes | QMessageBox.No
        )

        if answer == QMessageBox.Yes:
            self.reset_cube()
            self.toast.show_message("↺  Cube reset")

    def reset_cube(self):
        self.faces.clear()
        self.edit = ["Unknown"] * 9
        self.manual_overrides.clear()
        self.scan_frozen = False

        self.invalidate_solution()
        self.refresh_stickers()
        self.update_display()
        self.sync_auto_badge()
