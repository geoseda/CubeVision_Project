import sys
import json
import html
from pathlib import Path
from collections import Counter

import cv2

from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, QPropertyAnimation, QRectF, QSize
)
from PySide6.QtGui import (
    QImage, QPixmap, QPainter, QColor, QPainterPath,
    QFont, QPen, QShortcut, QKeySequence, QIcon
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QFrame,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QMessageBox, QFileDialog, QCheckBox,
    QProgressBar, QSlider, QButtonGroup, QSizePolicy,
    QGraphicsOpacityEffect
)

from color_recognition import COLORS, SYMBOLS, sample_face, annotate

try:
    from rubik_solver import Cube, init_solver, solve
    SOLVER_ERROR = None
except ImportError as exc:
    Cube = None
    init_solver = None
    solve = None
    SOLVER_ERROR = str(exc)

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------

# Icon files are loaded relative to this script, not the terminal directory.
ICON_DIRECTORY = Path(__file__).resolve().parent
ICON_FILES = {
    "logo": ("logo icon.png",),
    "accessibility": ("accesibility icon.png", "accessibility icon.png"),
    "capture": ("capture face icon.png",),
    "coach": ("cubecoach icon.png",),
    "ghost": ("ghost cube icon.png",),
    "import": ("import icon.png", "import image icon.png"),
    "progress": ("progress icon.png",),
    "restart": ("resstart cam icon.png", "restart cam icon.png", "restart camera icon.png"),
    "save": ("save face icon.png",),
}


def icon_path(name):
    for filename in ICON_FILES.get(name, ()):
        path = ICON_DIRECTORY / filename
        if path.is_file():
            return path
    # Also support capitalization differences and hidden Windows extensions.
    try:
        files = {f.name.casefold(): f for f in ICON_DIRECTORY.iterdir() if f.is_file()}
        for filename in ICON_FILES.get(name, ()):
            for candidate in (filename, filename + ".png"):
                if candidate.casefold() in files:
                    return files[candidate.casefold()]
    except OSError:
        pass
    return None


def app_icon(name):
    path = icon_path(name)
    return QIcon(str(path)) if path else QIcon()


FACES = ["U", "R", "F", "D", "L", "B"]

NAMES = {
    "U": "Up",
    "R": "Right",
    "F": "Front",
    "D": "Down",
    "L": "Left",
    "B": "Back"
}

GUIDES = {
    "U": "UP: Keep the BACK edge at the top.",
    "R": "RIGHT: Keep the UP edge at the top.",
    "F": "FRONT: Keep the UP edge at the top.",
    "D": "DOWN: Keep the FRONT edge at the top.",
    "L": "LEFT: Keep the UP edge at the top.",
    "B": "BACK: Keep the UP edge at the top."
}

PATTERNS = {
    "White": "XXX",
    "Yellow": "***",
    "Red": "===",
    "Orange": "+++",
    "Blue": "|||",
    "Green": "///"
}

MODE_INFO = {
    "Symbols": (
        "◆",
        "Shapes are drawn on every sticker. "
        "Ideal for color-blind users."
    ),
    "Patterns": (
        "▦",
        "Texture codes such as XXX or /// "
        "that can be read without color."
    ),
    "Color Names": (
        "Aa",
        "Plain-text color names written "
        "on every sticker."
    ),
    "Original Colors": (
        "🎨",
        "Real colors only, with no overlays."
    )
}

TAB_SCANNER = 0
TAB_ACCESS = 1
TAB_NET = 2
TAB_COACH = 3
TAB_PROGRESS = 4


# ----------------------------------------------------------------------
# Theme
# ----------------------------------------------------------------------

STYLE = """
QMainWindow {
    background: #0A0F1F;
}

QWidget#root {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0A0F1F, stop:1 #111C3A
    );
}

QWidget {
    color: #E2E8F0;
    font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial;
    font-size: 13px;
}

QLabel { background: transparent; }

QDialog, QMessageBox { background: #0F172A; }

QToolTip {
    background: #1E293B;
    color: #F1F5F9;
    border: 1px solid #475569;
    padding: 6px 8px;
}

/* ---------- Typography ---------- */
QLabel#appTitle {
    font-size: 24px;
    font-weight: 800;
    color: #F8FAFC;
}
QLabel[role="title"] {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 700;
}
QLabel[role="muted"] { color: #94A3B8; }
QLabel[role="hint"]  { color: #94A3B8; font-size: 12px; }
QLabel[role="big"] {
    font-size: 30px;
    font-weight: 800;
    color: #F8FAFC;
}
QLabel[role="guide"] {
    background: rgba(99, 102, 241, 0.14);
    border: 1px solid rgba(99, 102, 241, 0.40);
    border-radius: 12px;
    padding: 8px 14px;
    color: #C7D2FE;
}

QLabel#logo {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #6366F1, stop:1 #06B6D4
    );
    border-radius: 16px;
    color: white;
    font-size: 20px;
    font-weight: 800;
}

/* ---------- Cards ---------- */
QFrame#card {
    background: rgba(21, 30, 52, 0.88);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 18px;
}
QFrame#faceCard {
    background: rgba(15, 23, 42, 0.60);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 14px;
}
QFrame#moveCard {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(99, 102, 241, 0.32),
        stop:1 rgba(6, 182, 212, 0.18)
    );
    border: 1px solid rgba(129, 140, 248, 0.45);
    border-radius: 22px;
}

QLabel#cameraView {
    background: #020617;
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 18px;
    color: #64748B;
    font-size: 16px;
}

QLabel#bigMove {
    font-size: 88px;
    font-weight: 800;
    color: #F8FAFC;
}
QLabel#moveDesc {
    font-size: 17px;
    color: #C7D2FE;
}

/* ---------- Status pills & badges ---------- */
QLabel[pill="true"] {
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.40);
    border-radius: 12px;
    padding: 10px 14px;
    color: #BAE6FD;
}
QLabel[pill="true"][level="ok"] {
    background: rgba(34, 197, 94, 0.12);
    border: 1px solid rgba(34, 197, 94, 0.45);
    color: #BBF7D0;
}
QLabel[pill="true"][level="warn"] {
    background: rgba(250, 204, 21, 0.12);
    border: 1px solid rgba(250, 204, 21, 0.45);
    color: #FEF08A;
}
QLabel[pill="true"][level="error"] {
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.50);
    color: #FECACA;
}

QLabel[badge] {
    border-radius: 10px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 700;
}
QLabel[badge="on"] {
    background: rgba(34, 197, 94, 0.16);
    border: 1px solid rgba(34, 197, 94, 0.55);
    color: #86EFAC;
}
QLabel[badge="off"], QLabel[badge="frozen"] {
    background: rgba(250, 204, 21, 0.14);
    border: 1px solid rgba(250, 204, 21, 0.55);
    color: #FDE047;
}
QLabel[badge="pending"] {
    background: rgba(100, 116, 139, 0.18);
    border: 1px solid rgba(100, 116, 139, 0.55);
    color: #CBD5E1;
}

/* ---------- Buttons ---------- */
QPushButton {
    background: rgba(51, 65, 85, 0.70);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 12px;
    padding: 10px 16px;
    font-weight: 600;
    color: #E2E8F0;
}
QPushButton:hover   { background: rgba(71, 85, 105, 0.90); }
QPushButton:pressed { background: rgba(30, 41, 59, 1.0); }
QPushButton:focus   { border: 2px solid #7DD3FC; }
QPushButton:disabled {
    background: rgba(30, 41, 59, 0.50);
    color: #64748B;
    border: 1px solid rgba(100, 116, 139, 0.25);
}

QPushButton[variant="primary"] {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:1 #06B6D4
    );
    border: none;
    color: white;
}
QPushButton[variant="primary"]:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #818CF8, stop:1 #22D3EE
    );
}
QPushButton[variant="primary"]:focus { border: 2px solid #E0F2FE; }
QPushButton[variant="primary"]:disabled {
    background: rgba(51, 65, 85, 0.6);
    color: #64748B;
}

QPushButton[variant="danger"] {
    background: rgba(239, 68, 68, 0.14);
    border: 1px solid rgba(239, 68, 68, 0.50);
    color: #FCA5A5;
}
QPushButton[variant="danger"]:hover {
    background: rgba(239, 68, 68, 0.30);
}

QPushButton[variant="ghost"] {
    background: transparent;
    border: 1px solid rgba(148, 163, 184, 0.30);
    color: #CBD5E1;
}
QPushButton[variant="ghost"]:hover {
    background: rgba(148, 163, 184, 0.14);
}

QPushButton[facelink="true"] {
    background: transparent;
    border: none;
    color: #A5B4FC;
    padding: 2px 4px;
    text-align: left;
    font-weight: 700;
}
QPushButton[facelink="true"]:hover { color: white; }

/* Segmented chips (face selector & display mode) */
QPushButton[chip="true"] {
    background: rgba(30, 41, 59, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 12px;
    padding: 6px 8px;
    min-width: 46px;
    font-size: 12px;
}
QPushButton[chip="true"][saved="true"] {
    border: 1px solid rgba(34, 197, 94, 0.70);
    color: #86EFAC;
}
QPushButton[chip="true"]:checked {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #6366F1, stop:1 #06B6D4
    );
    border: none;
    color: white;
}

/* Solution move chips */
QPushButton[movechip] {
    border-radius: 10px;
    padding: 7px 0px;
    min-width: 46px;
    font-weight: 700;
}
QPushButton[movechip="done"] {
    background: rgba(34, 197, 94, 0.12);
    border: 1px solid rgba(34, 197, 94, 0.35);
    color: #86EFAC;
}
QPushButton[movechip="current"] {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #6366F1, stop:1 #06B6D4
    );
    border: none;
    color: white;
}

/* ---------- Tabs ---------- */
QTabWidget::pane { border: none; background: transparent; }
QTabBar { background: transparent; }
QTabBar::tab {
    background: rgba(30, 41, 59, 0.70);
    color: #94A3B8;
    padding: 10px 22px;
    margin-right: 8px;
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.15);
    font-weight: 600;
}
QTabBar::tab:hover {
    color: #E2E8F0;
    background: rgba(51, 65, 85, 0.85);
}
QTabBar::tab:selected {
    color: white;
    border: none;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:1 #06B6D4
    );
}

/* ---------- Progress & slider ---------- */
QProgressBar {
    background: rgba(148, 163, 184, 0.18);
    border: none;
    border-radius: 5px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    border-radius: 5px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:1 #22D3EE
    );
}

QSlider::groove:horizontal {
    height: 6px;
    background: #334155;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #6366F1;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: white;
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QStatusBar { background: transparent; color: #94A3B8; }
QStatusBar::item { border: none; }

/* ---------- Toast ---------- */
QLabel#toast {
    background: rgba(15, 23, 42, 0.96);
    border: 1px solid rgba(56, 189, 248, 0.60);
    border-radius: 16px;
    padding: 12px 22px;
    color: #F1F5F9;
    font-size: 14px;
    font-weight: 600;
}
QLabel#toast[level="ok"]   { border: 1px solid rgba(34, 197, 94, 0.80); }
QLabel#toast[level="warn"] { border: 1px solid rgba(250, 204, 21, 0.80); }
"""


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def repolish(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def rgb_of(color):
    r, g, b = COLORS.get(color, (71, 85, 105))
    return int(r), int(g), int(b)


def ideal_text(rgb):
    r, g, b = rgb
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#0F172A" if luminance > 140 else "#FFFFFF"


def rounded_pixmap(pixmap, radius, badge=None):
    out = QPixmap(pixmap.size())
    out.fill(Qt.transparent)

    painter = QPainter(out)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    path = QPainterPath()
    path.addRoundedRect(QRectF(out.rect()), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.setClipping(False)

    if badge:
        text, color = badge

        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)

        width = painter.fontMetrics().horizontalAdvance(text) + 40
        height = 28

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(15, 23, 42, 205))
        painter.drawRoundedRect(
            QRectF(14, 14, width, height), 14, 14
        )

        painter.setBrush(QColor(color))
        painter.drawEllipse(
            QRectF(24, 14 + height / 2 - 4, 8, 8)
        )

        painter.setPen(QColor("white"))
        painter.drawText(
            QRectF(38, 14, width - 28, height),
            Qt.AlignVCenter | Qt.AlignLeft,
            text
        )

    painter.end()
    return out


# ----------------------------------------------------------------------
# Custom widgets
# ----------------------------------------------------------------------

