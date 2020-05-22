from argparse import ArgumentParser
from logging import warning, info
from queue import Queue
from pathlib import Path
from re import compile
from threading import Thread
from typing import List
from tempfile import _get_candidate_names

from app.pdf_generator import process

try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        def __init__(self):
            info('You can install tqdm for display progress bar')

        def update(self, n=1):
            pass


_args = ArgumentParser()
_args.add_argument('-i', '--input', help="Read html's list into file. Each line is html file!", type=str, default=None)
_args.add_argument('html', type=str, nargs='*', help='Path to html file')
_args.add_argument('-d', '--destination', help='Destination directory', type=str, default='.')
_args.add_argument('-c', '--concurrency', help='Max parallel processing threads', default=2, type=int)

RE = compile(r'^(.+)\.html?$')


def process_one_file(file: Path, dst: Path):
    if not file.is_file():
        warning(f'Path {file} is not file')
        return

    names = _get_candidate_names()

    file = file.absolute()

    pdf_filename = f'{RE.search(file.name).group(1)}.pdf'

    while True:
        pdf_path = dst.joinpath(pdf_filename)

        if not pdf_path.is_file():
            break

        pdf_filename = f'{RE.search(file.name).group(1)}~{next(names)}.pdf'



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
            # while True:
            process_one_file(*self.queue.get())
            tq and tq.update()
            self.queue.task_done()

    queue = Queue()

    for i in range(max(args.concurrency, 1)):
        daemon = Process(queue)
        daemon.setDaemon(True)
        daemon.start()

    for file in files:
        queue.put((file, dst))
    queue.join()

    return 0 if queue.all_tasks_done else 1


def files_from_file(file: Path):
    with open(str(file), 'r') as r:
        return filter(lambda x: len(x) > 0, r.readlines())


if __name__ == '__main__':
    args = _args.parse_args()

    if args.input is not None:
        files = files_from_file(Path(args.input))
    else:
        files = list(map(Path, filter(lambda x: len(x) > 0, args.html)))

    files_count = len(files)

    if files_count < 1:
        warning('Html files list is empty')
        exit(1)

    tq = None
    if files_count > 1:
        tq = tqdm(files_count)

    dst = Path(args.destination)
    dst.mkdir(parents=True, exist_ok=True)

    exit(main(files, dst))
