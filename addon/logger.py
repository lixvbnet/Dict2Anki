import logging
from logging.handlers import BufferingHandler

from PyQt5.QtCore import pyqtSignal, QObject


class LogEventEmitter(QObject):
    newRecord = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)

    def emit(self, obj):
        self.newRecord.emit(obj)


class MyBufferingHandler(BufferingHandler):
    def __init__(self, parent, capacity=20):
        """
        :param capacity: number of messages (i.e. log records) we can hold in buffer.
        """
        self.eventEmitter = LogEventEmitter(parent)
        super().__init__(capacity)
        formatter = Formatter('[$name][$levelname] $message', style="$")
        self.setFormatter(formatter)

    def flush(self):
        if not self.buffer:
            return
        msgs = []
        for record in self.buffer:
            msgs.append(self.format(record))
        self.eventEmitter.emit("\n".join(msgs))
        super().flush()


class Formatter(logging.Formatter):
    def formatException(self, ei):
        result = super(Formatter, self).formatException(ei)
        return result

    def format(self, record):
        s = super(Formatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '')
        return s
