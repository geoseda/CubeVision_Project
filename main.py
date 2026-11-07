from shared import *
from widgets import *
from solver_worker import SolverWorker
from ui_scanner import UiScannerMixin
from ui_accessibility import UiAccessibilityMixin
from ui_ghostcube import UiGhostcubeMixin
from ui_coach import UiCoachMixin
from ui_progress import UiProgressMixin
from camera import CameraMixin
from face_manager import FaceManagerMixin
from accessibility import AccessibilityMixin
from display import DisplayMixin
from solver import SolverMixin
from project_data import ProjectDataMixin
from shortcuts import ShortcutsMixin

class CubeVision(QMainWindow, UiScannerMixin, UiAccessibilityMixin, UiGhostcubeMixin, UiCoachMixin, UiProgressMixin, CameraMixin, FaceManagerMixin, AccessibilityMixin, DisplayMixin, SolverMixin, ProjectDataMixin, ShortcutsMixin):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "CubeVision X - Accessible Rubik's Cube Assistant"
        )
        self.setMinimumSize(1100, 760)
        self.resize(1240, 820)

        self.camera = None
        self.frame = None
        self.from_image = False

        self.live = ["Unknown"] * 9
        self.edit = ["Unknown"] * 9

        self.manual_overrides = set()
        self.auto_detect_enabled = True
        self.scan_frozen = False

        self.faces = {}
        self.moves = []
        self.move_index = 0
        self.worker = None

        self.current_face = "U"

        self.mode = "Symbols"
        self.voice_enabled = True
        self.voice_rate = 165

        self.setStyleSheet(STYLE)
        self.setWindowIcon(app_icon("logo"))

        root = QWidget()
        root.setObjectName("root")

        outer = QVBoxLayout(root)
        outer.setContentsMargins(24, 18, 24, 8)
        outer.setSpacing(12)

        outer.addWidget(self.build_header())

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setDrawBase(False)
        self.tabs.setIconSize(QSize(27, 27))
        outer.addWidget(self.tabs, 1)

        outer.addWidget(self.label(
            "Shortcuts:  C capture  ·  S save face  ·  "
            "V read face aloud  ·  P / N previous / next move  "
            "·  M speak move",
            "hint"
        ))

        self.setCentralWidget(root)

        self.build_scanner()
        self.build_accessibility()
        self.build_net()
        self.build_coach()
        self.build_progress()

        self.toast = Toast(self)

        self.setup_shortcuts()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)

        self.refresh_stickers()
        self.update_display()
        self.start_camera()

    def label(self, text="", role=None, wrap=False,
              align=None, name=None):
        lbl = QLabel(text)

        if role:
            lbl.setProperty("role", role)

        if wrap:
            lbl.setWordWrap(True)

        if align is not None:
            lbl.setAlignment(align)

        if name:
            lbl.setObjectName(name)

        return lbl

    def pill(self, text):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setProperty("pill", "true")
        lbl.setProperty("level", "info")
        return lbl

    def button(self, layout, title, callback,
               variant=None, tip=None, icon_name=None):
        btn = QPushButton(title)
        if icon_name and not app_icon(icon_name).isNull():
            btn.setIcon(app_icon(icon_name))
            btn.setIconSize(QSize(25, 25))

        if variant:
            btn.setProperty("variant", variant)

        if tip:
            btn.setToolTip(tip)

        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def card(self, title=None):
        frame = QFrame()
        frame.setObjectName("card")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 18)
        layout.setSpacing(10)

        if title:
            layout.addWidget(self.label(title, "title"))

        return frame, layout

    def set_status(self, lbl, text, level="info"):
        lbl.setText(text)
        lbl.setProperty("level", level)
        repolish(lbl)

    def set_scan_status(self, text, level="info"):
        self.set_status(self.scan_status, text, level)

    def sync_auto_badge(self):
        if not self.auto_detect_enabled:
            state, text = "off", "AUTO DETECTION: OFF"
        elif self.scan_frozen:
            state, text = "frozen", "CAPTURED / FROZEN"
        else:
            state, text = "on", "AUTO DETECTION: ON"

        self.auto_status.setText(text)
        self.auto_status.setProperty("badge", state)
        repolish(self.auto_status)

    def build_header(self):
        bar = QWidget()
        row = QHBoxLayout(bar)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)

        logo = QLabel("CX")
        logo.setObjectName("logo")
        logo.setFixedSize(52, 52)
        logo.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(str(icon_path("logo"))) if icon_path("logo") else QPixmap()
        if not logo_pixmap.isNull():
            logo.setText("")
            logo.setStyleSheet("background: transparent; border: none;")
            logo.setPixmap(logo_pixmap.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        row.addWidget(logo)

        titles = QVBoxLayout()
        titles.setSpacing(0)
        titles.addWidget(self.label(
            "CubeVision X", name="appTitle"
        ))
        titles.addWidget(self.label(
            "Accessible Rubik's Cube Assistant", "muted"
        ))
        row.addLayout(titles)

        row.addStretch()

        progress = QVBoxLayout()
        progress.setSpacing(6)

        self.header_label = self.label(
            "FACES SAVED  0 / 6", "title",
            align=Qt.AlignRight
        )
        progress.addWidget(self.header_label)

        self.header_progress = QProgressBar()
        self.header_progress.setRange(0, 6)
        self.header_progress.setTextVisible(False)
        self.header_progress.setFixedSize(240, 10)
        progress.addWidget(self.header_progress)

        row.addLayout(progress)

        return bar

    def resizeEvent(self, event):
        super().resizeEvent(event)

        toast = getattr(self, "toast", None)

        if toast is not None and toast.isVisible():
            toast.reposition()

    def closeEvent(self, event):
        self.timer.stop()

        if self.camera is not None:
            self.camera.release()

        if self.worker is not None:
            if self.worker.isRunning():
                self.worker.wait()

        event.accept()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = CubeVision()
    window.show()

    sys.exit(app.exec())