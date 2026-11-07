from shared import *
from widgets import *
from solver_worker import SolverWorker

class CameraMixin:
    def start_camera(self):
        if hasattr(self, "timer"):
            self.timer.stop()

        if self.camera is not None:
            self.camera.release()

        self.from_image = False

        self.camera = cv2.VideoCapture(
            0,
            cv2.CAP_DSHOW
        )

        if not self.camera.isOpened():
            self.camera.release()
            self.camera = cv2.VideoCapture(0)

        if self.camera.isOpened():
            self.scan_frozen = False
            self.sync_auto_badge()
            self.timer.start(60)
            self.set_scan_status(
                "Camera ready. Align the cube face. "
                "Colors update automatically.",
                "ok"
            )
        else:
            self.camera_label.setPixmap(QPixmap())
            self.camera_label.setText(
                "🚫   No camera found\n\n"
                "Plug one in and press Restart Camera,\n"
                "or import a photo of your cube."
            )
            self.set_scan_status(
                "Camera unavailable. Import an image.",
                "warn"
            )

    def update_camera(self):
        if self.camera is None:
            return

        success, frame = self.camera.read()

        if success:
            self.process_frame(frame)

    def draw_overlay(self, frame, rects):
        if self.mode == "Symbols":
            return annotate(frame, self.live)

        display = frame.copy()

        for color, rect in zip(self.live, rects):
            x1, y1, x2, y2 = rect

            cv2.rectangle(
                display,
                (x1, y1),
                (x2, y2),
                (255, 255, 255),
                2
            )

            if self.mode == "Original Colors":
                continue

            if color in COLORS:
                bgr = tuple(
                    int(v) for v in COLORS[color][::-1]
                )

                cv2.rectangle(
                    display,
                    (x1 + 3, y1 + 3),
                    (x2 - 3, y2 - 3),
                    bgr,
                    3
                )

            if self.mode == "Patterns":
                text = PATTERNS.get(color, "???")
            else:
                text = color

            pos = (
                x1 + 6,
                y1 + int((y2 - y1) * 0.6)
            )

            cv2.putText(
                display,
                text,
                pos,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                4
            )

            cv2.putText(
                display,
                text,
                pos,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

        return display

    def process_frame(self, frame):
        self.frame = frame.copy()

        self.live, rects = sample_face(frame)

        if self.auto_detect_enabled and not self.scan_frozen:
            changed = False

            for i, color in enumerate(self.live):
                if i not in self.manual_overrides:
                    if self.edit[i] != color:
                        self.edit[i] = color
                        changed = True

            if changed:
                self.refresh_stickers()

        display = self.draw_overlay(frame, rects)

        rgb = cv2.cvtColor(
            display,
            cv2.COLOR_BGR2RGB
        )

        h, w = rgb.shape[:2]

        image = QImage(
            rgb.data,
            w,
            h,
            3 * w,
            QImage.Format_RGB888
        ).copy()

        pixmap = QPixmap.fromImage(image).scaled(
            self.camera_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        if self.from_image:
            badge = ("PHOTO", "#38BDF8")
        elif self.scan_frozen:
            badge = ("LIVE · FACE LOCKED", "#FACC15")
        else:
            badge = ("LIVE", "#EF4444")

        self.camera_label.setPixmap(
            rounded_pixmap(pixmap, 18, badge)
        )

    def capture_face(self):
        if self.frame is None:
            QMessageBox.warning(
                self,
                "No Image",
                "Start the camera or import an image."
            )
            return

        self.scan_frozen = True

        for i, color in enumerate(self.live):
            if i not in self.manual_overrides:
                self.edit[i] = color

        self.refresh_stickers()

        self.set_scan_status(
            "Face captured and frozen. "
            "Correct any sticker manually, then Save.",
            "warn"
        )

        self.sync_auto_badge()

    def import_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Cube Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not path:
            return

        frame = cv2.imread(path)

        if frame is None:
            QMessageBox.warning(
                self,
                "Image Error",
                "Cannot open the selected image."
            )
            return

        self.timer.stop()
        self.from_image = True
        self.scan_frozen = False
        self.process_frame(frame)
        self.capture_face()
