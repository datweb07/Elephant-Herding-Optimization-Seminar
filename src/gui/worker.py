import logging
from threading import Event
from time import perf_counter

from PySide6.QtCore import QThread, Signal


class OptimizerWorker(QThread):
    progress = Signal(object, object)
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, optimizer, save_population, parent=None):
        super().__init__(parent)
        self.optimizer = optimizer
        self.save_population = save_population
        self.stop_requested = Event()
        self.last_update = 0.0

    def report(self, row, snapshot):
        now = perf_counter()
        if row.number == 0 or now - self.last_update >= 0.15:
            self.progress.emit(row, snapshot)
            self.last_update = now

    def run(self):
        try:
            result = self.optimizer.run(
                save_population=self.save_population, on_generation=self.report,
                should_stop=self.stop_requested.is_set,
            )
        except Exception as error:
            logging.exception("EHO worker failed")
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(result)
