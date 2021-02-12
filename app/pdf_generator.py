import sys
from base64 import decodebytes, encodebytes
from logging import error
from multiprocessing import Process, Queue

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

from ._logger import get_logger

__all__ = ['process']


logger = get_logger()


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

        logger.info('Generate "{}": start'.format(url))

        def writer(data):
            queue.put(encodebytes(data))

        _generate_pdf(url, writer)

        logger.info('Generate "{}": stop'.format(url))

    try:
        p = Process(target=_process, args=(url, queue, ))

        p.start()
        _data = queue.get()
        data = decodebytes(_data)
        p.join(timeout)

        return data
    except Exception as e:
        error(e)

        logger.error('pdf_generator.process error: {}'.format(*e.args))

        return None
