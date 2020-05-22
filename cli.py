from argparse import ArgumentParser
from logging import warning, error, info
from pathlib import Path
from queue import Queue
from re import compile
from tempfile import _get_candidate_names
from threading import Thread
from typing import List

from app.pdf_generator import process

_args = ArgumentParser()
_args.add_argument('-i', '--input', help="Read html's list into file. Each line is html file!", type=str, default=None)
_args.add_argument('html', type=str, nargs='*', help='Path to html file')
_args.add_argument('-d', '--destination', help='Destination directory', type=str, default='.')
_args.add_argument('-c', '--concurrency', help='Max parallel processing threads', default=2, type=int)

RE = compile(r'^(.+)\.html?$')


def process_one_file(file: Path, dst: Path, idx, *args):
    if not file.is_file():
        warning(f'Path {file} is not a file')
        return

    names = _get_candidate_names()

    file = file.absolute()

    while True:
        pdf_filename = f'{RE.search(file.name).group(1)}~{next(names)}.pdf'

        pdf_path = dst.joinpath(pdf_filename)

        if not pdf_path.is_file():
            break

    info('{}:{}'.format(idx, file))

    data = process(f'file://{file}')

    if data is None:
        warning(f'Data is none for file {file}')
        return

    pdf_path.write_bytes(data)


def main(files: List[Path], dst: Path):

    class Process(Thread):
        _queue = None

        def __init__(self, queue):
            super().__init__()
            self.queue = queue

        def run(self):
            while True:
                try:
                    process_one_file(*self.queue.get())
                except Exception as e:
                    error(e)

                self.queue.task_done()

    queue = Queue()

    for i in range(max(args.concurrency, 1)):
        daemon = Process(queue)
        daemon.setDaemon(True)
        daemon.start()

    for idx, file in enumerate(files):
        queue.put((file, dst, idx))

    queue.join()


def files_from_file(file: Path):
    with open(str(file), 'r') as r:
        return filter(lambda x: len(x) > 0, r.readlines())


if __name__ == '__main__':
    args = _args.parse_args()

    if args.input is not None:
        files = map(Path, map(lambda x: f'{x}'.strip(), files_from_file(Path(args.input))))
    else:
        files = map(Path, filter(lambda x: len(x) > 0, args.html))

    files = list(files)
    files_count = len(files)

    if files_count < 1:
        warning('Html files list is empty')
        exit(1)

    dst = Path(args.destination)
    dst.mkdir(parents=True, exist_ok=True)

    main(files, dst)
