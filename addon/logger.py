import logging
from logging.handlers import BufferingHandler
import threading

from aqt.qt import pyqtSignal, QObject


def call_at_interval(interval, func, *args):
    """utility function to start a thread and call a function every `interval` seconds."""
    stopped = threading.Event()

    # actual thread function
    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)

    t = threading.Thread(target=loop)
    t.daemon = True
    t.start()
    return stopped.set, t


class LogEventEmitter(QObject):
    newRecord = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)

    def emit(self, obj):
        self.newRecord.emit(obj)


class TimedBufferingHandler(BufferingHandler):
    def __init__(self, parent, capacity=20, flush_interval=3):
        """
        :param capacity: number of messages (i.e. log records) we can hold in buffer.
        :param flush_interval: flush logs every `flush_interval` seconds
        """
        super().__init__(capacity)
        self.eventEmitter = LogEventEmitter(parent)
        formatter = Formatter('[$name][$levelname] $message', style="$")
        self.setFormatter(formatter)
        # flush logs every `flush_interval` seconds
        self.timer_stopper, self.timer_thread = call_at_interval(flush_interval, self.flush)

    def flush(self):
        if not self.buffer:
            return
        try:
            msgs = []
            for record in self.buffer:
                msgs.append(self.format(record))
            if self.eventEmitter:
                self.eventEmitter.emit("\n".join(msgs))
            super().flush()
        except RuntimeError or AttributeError:
            pass

    def close(self):
        self.timer_stopper()
        super().close()


class Formatter(logging.Formatter):
    def formatException(self, ei):
        result = super(Formatter, self).formatException(ei)
        return result

    def format(self, record):
        s = super(Formatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '')
        return s
