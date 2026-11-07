from shared import *
from widgets import *
from solver_worker import SolverWorker

class ShortcutsMixin:
    def setup_shortcuts(self):
        # Single letters are used on purpose so that the usual
        # keyboard behavior (Space/Enter on buttons, arrows on
        # tabs) stays untouched for keyboard-only users.
        bindings = {
            "C": self.shortcut_capture,
            "S": self.shortcut_save,
            "V": self.shortcut_read,
            "P": self.shortcut_previous,
            "N": self.shortcut_next,
            "M": self.shortcut_speak
        }

        self.shortcuts = []

        for key, callback in bindings.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)

    def shortcut_capture(self):
        if self.tabs.currentIndex() == TAB_SCANNER:
            self.capture_face()

    def shortcut_save(self):
        if self.tabs.currentIndex() == TAB_SCANNER:
            self.save_face()

    def shortcut_read(self):
        if self.tabs.currentIndex() == TAB_SCANNER:
            self.read_face()

    def shortcut_previous(self):
        if self.tabs.currentIndex() == TAB_COACH:
            self.previous_move()

    def shortcut_next(self):
        if self.tabs.currentIndex() == TAB_COACH:
            self.next_move()

    def shortcut_speak(self):
        if self.tabs.currentIndex() == TAB_COACH:
            self.speak_move()
