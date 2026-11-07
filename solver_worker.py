from shared import *

class SolverWorker(QThread):
    success = Signal(str)
    failure = Signal(str)

    def __init__(self, facelets):
        super().__init__()
        self.facelets = facelets

    def run(self):
        try:
            cube = Cube.from_string(self.facelets)
            verified = cube.verify()

            if verified is not True:
                self.failure.emit(str(verified))
                return

            if cube.is_solved():
                self.success.emit("")
                return

            init_solver()
            solution = solve(cube)

            if solution is None:
                self.failure.emit("No solution found.")
            else:
                if isinstance(solution, (list, tuple)):
                    result = " ".join(map(str, solution))
                else:
                    result = str(solution)

                self.success.emit(result)

        except Exception as exc:
            self.failure.emit(str(exc))
