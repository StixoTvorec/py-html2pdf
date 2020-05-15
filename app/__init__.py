import os
import zipfile
from logging import Logger
from pathlib import Path
from random import randint
from shutil import rmtree

from flask import Flask, request, Response, abort, render_template
from werkzeug.datastructures import FileStorage

from .pdf_generator import process


app = Flask('app')
app.debug = bool(os.environ.get("DEBUG"))
logger = app.logger  # type: Logger

temp_dir = Path(__file__).parent.parent.joinpath('var')
temp_dir.mkdir(exist_ok=True)


@app.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def generate():
    file = request.files.get('html', None)  # type: FileStorage

    logger.info(f'Connection from ip: {request.remote_addr}')

    if file is None:
        logger.warning(f'File not exists in request')
        abort(500)

    rnd = randint(1000000, 2000000)
    rnd_dir = f'dir_archive_{rnd}'

    logger.info(f'Processing {rnd}')

    temp_file = temp_dir.joinpath(f'archive_{rnd}.zip')
    temp_extracted = temp_dir.joinpath(rnd_dir)
    temp_extracted.mkdir()

    temp_file.write_bytes(file.stream.read())

    try:
        templates = temp_extracted.absolute()

        zipfile.ZipFile(temp_file).extractall(str(temp_extracted))

        data = process(f'file://{templates}/index.html')

        rmtree(str(temp_extracted))
        temp_file.unlink()

        if data is None:
            abort(500)

        return Response(data, headers={
            'Content-Type': 'application/pdf',
            'Content-Disposition': 'attachment; filename=html.pdf',
        })
    except Exception as e:
        logger.error(e)

        try:
            temp_file.unlink()
        except:
            pass
        try:
            rmtree(str(temp_extracted))
        except:
            pass

        abort(500)


if __name__ == '__main__':
    app.run('127.0.0.1', '8082')
