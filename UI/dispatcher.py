from SkinningTools.UI.qt_util import *
import Queue

class ThreadDispatcher(QThread):

    def __init__(self, parent):
        QThread.__init__(self)
        self.idle_loop = Queue.Queue()
        self.parent = parent

    def run(self):
        while True:
            callback = self.idle_loop.get()
            if callback is None:
                break
            QApplication.postEvent(self.parent, _Event(callback))

        return

    def stop(self):
        self.idle_loop.put(None)
        self.wait()
        return

    def idle_add(self, func, *args, **kwargs):

        def idle():
            func(*args, **kwargs)
            return False

        self.idle_loop.put(idle)
        if not self.isRunning():
            self.start()

class _Event(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callback):
        QEvent.__init__(self, _Event.EVENT_TYPE)
        self.callback = callback