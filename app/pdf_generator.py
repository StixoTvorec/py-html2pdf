import sys
from base64 import decodebytes, encodebytes
from multiprocessing import Process, Queue
from logging import error

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

__all__ = ['process']


def _generate_pdf(url: str, callback: callable):

    app = QtWidgets.QApplication(sys.argv)
    loader = QtWebEngineWidgets.QWebEngineView()
    loader.setZoomFactor(1)

    def _quit(*args, **kwargs):
        app.quit()

    loader.page().pdfPrintingFinished.connect(_quit)
    loader.load(QtCore.QUrl(url))

    def fill_data(_d):
        callback(_d)
        app.quit()

    def emit_pdf(finished):
        loader.page().printToPdf(fill_data)

    loader.loadFinished.connect(emit_pdf)

    app.exec_()


def process(url: str, timeout: int = 5):
    queue = Queue()

    def _process(url: str, queue: Queue):

        def writer(data):
            queue.put(encodebytes(data))

        _generate_pdf(url, writer)

    try:
        p = Process(target=_process, args=(url, queue, ))

        p.start()
        data = decodebytes(queue.get())
        p.join(timeout)

        return data
    except Exception as e:
        error(e)
        return None
