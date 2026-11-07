from shared import *

class ToggleSwitch(QCheckBox):
    """iOS-style on/off switch (keyboard accessible)."""

    def __init__(self, checked=False):
        super().__init__()
        self.setChecked(checked)
        self.setFixedSize(48, 28)
        self.setCursor(Qt.PointingHandCursor)

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track = QRectF(self.rect()).adjusted(1, 1, -1, -1)

        painter.setPen(Qt.NoPen)
        painter.setBrush(
            QColor("#22C55E")
            if self.isChecked()
            else QColor("#475569")
        )
        painter.drawRoundedRect(track, 13, 13)

        diameter = 20
        x = (
            self.width() - diameter - 5
            if self.isChecked()
            else 5
        )

        painter.setBrush(QColor("white"))
        painter.drawEllipse(
            QRectF(
                x,
                (self.height() - diameter) / 2,
                diameter,
                diameter
            )
        )

        if self.hasFocus():
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor("#7DD3FC"), 2))
            painter.drawRoundedRect(track, 13, 13)


class StickerButton(QPushButton):
    """A big, tactile sticker tile painted by hand."""

    def __init__(self, index):
        super().__init__()

        self.index = index
        self.color_name = "Unknown"
        self.symbol = "?"
        self.locked = False

        self.setMinimumSize(68, 68)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Click to cycle this sticker's color")

    def set_sticker(self, color, symbol, locked):
        self.color_name = color
        self.symbol = symbol
        self.locked = locked

        state = ", locked" if locked else ""
        self.setAccessibleName(
            f"Sticker {self.index + 1}: {color}{state}"
        )

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        known = self.color_name in COLORS
        hovered = self.underMouse()

        rect = QRectF(self.rect()).adjusted(3, 3, -3, -3)

        if known:
            base = QColor(*rgb_of(self.color_name))
            text_color = QColor(
                ideal_text(rgb_of(self.color_name))
            )
        else:
            base = QColor("#334155")
            text_color = QColor("#CBD5E1")

        if self.isDown():
            base = base.darker(118)
        elif hovered:
            base = base.lighter(112)

        painter.setPen(Qt.NoPen)
        painter.setBrush(base)
        painter.drawRoundedRect(rect, 16, 16)

        if self.locked:
            pen = QPen(QColor("#FACC15"), 3)
        elif self.hasFocus():
            pen = QPen(QColor("#7DD3FC"), 3)
        elif hovered:
            pen = QPen(QColor("#FFFFFF"), 2)
        else:
            pen = QPen(QColor(255, 255, 255, 55), 1.5)

        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, 16, 16)

        painter.setPen(text_color)

        font = QFont(self.font())
        font.setBold(True)

        font.setPointSize(20)
        painter.setFont(font)
        painter.drawText(
            QRectF(
                rect.x(),
                rect.y() + rect.height() * 0.10,
                rect.width(),
                rect.height() * 0.50
            ),
            Qt.AlignCenter,
            self.symbol
        )

        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(
            QRectF(
                rect.x(),
                rect.y() + rect.height() * 0.60,
                rect.width(),
                rect.height() * 0.28
            ),
            Qt.AlignCenter,
            self.color_name if known else "Tap to set"
        )

        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)

        faded = QColor(text_color)
        faded.setAlpha(150)
        painter.setPen(faded)

        painter.drawText(
            rect.adjusted(9, 6, -9, -6),
            Qt.AlignTop | Qt.AlignLeft,
            str(self.index + 1)
        )

        if self.locked:
            painter.setPen(text_color)
            painter.drawText(
                rect.adjusted(9, 5, -9, -6),
                Qt.AlignTop | Qt.AlignRight,
                "🔒"
            )


class Toast(QLabel):
    """Small floating notification that fades in and out."""

    def __init__(self, parent):
        super().__init__(parent)

        self.setObjectName("toast")
        self.setAlignment(Qt.AlignCenter)
        self.hide()

        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)

        self.anim = QPropertyAnimation(
            self.effect,
            b"opacity",
            self
        )
        self.anim.finished.connect(self._finished)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._fade_out)

        self._hiding = False

    def show_message(self, text, level="info", msec=2600):
        self.setProperty("level", level)
        repolish(self)

        self.setText(text)
        self.adjustSize()
        self.reposition()

        self._hiding = False
        self.anim.stop()
        self.anim.setDuration(200)
        self.anim.setStartValue(self.effect.opacity())
        self.anim.setEndValue(1.0)

        self.show()
        self.raise_()
        self.anim.start()

        self.timer.start(msec)

    def reposition(self):
        parent = self.parentWidget()

        if parent is None:
            return

        self.move(
            (parent.width() - self.width()) // 2,
            parent.height() - self.height() - 56
        )

    def _fade_out(self):
        self._hiding = True
        self.anim.stop()
        self.anim.setDuration(450)
        self.anim.setStartValue(self.effect.opacity())
        self.anim.setEndValue(0.0)
        self.anim.start()

    def _finished(self):
        if self._hiding:
            self.hide()
