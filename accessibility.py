from shared import *
from widgets import *
from solver_worker import SolverWorker

class AccessibilityMixin:
    def change_mode(self, mode):
        self.mode = mode

        self.mode_buttons[mode].setChecked(True)
        self.set_status(
            self.mode_hint, MODE_INFO[mode][1], "info"
        )

        self.update_display()

    def change_rate(self, value):
        self.voice_rate = value
        self.rate_label.setText(
            f"Speech speed: {value} words / min"
        )

    def speak(self, text):
        if not self.voice_enabled:
            return

        if pyttsx3 is None:
            self.statusBar().showMessage(
                "Install pyttsx3 for voice assistance.",
                5000
            )
            return

        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.voice_rate)
            engine.say(text)
            engine.runAndWait()
            engine.stop()

        except Exception as exc:
            self.statusBar().showMessage(
                f"Voice error: {exc}",
                5000
            )
