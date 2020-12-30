import os
import zipfile
from logging import Logger
from pathlib import Path
from random import randint
from shutil import rmtree

from flask import Flask, request, Response, abort, render_template
from pyvirtualdisplay import Display
from werkzeug.datastructures import FileStorage

Display().start()

from .pdf_generator import process


app = Flask('app')
app.debug = bool(os.environ.get("DEBUG"))
logger = app.logger  # type: Logger

temp_dir = Path(__file__).parent.parent.joinpath('var')

try:
    for _item in temp_dir.iterdir():
        rmtree(str(_item))
except FileNotFoundError:
    pass

temp_dir.mkdir(exist_ok=True)


@app.route('/', methods=['GET'], )
def index_page():
    return Response(render_template('index.html'), status=418)


@app.route('/', methods=['POST'])
def generate():
    file = request.files.get('html', None)  # type: FileStorage

    logger.info(f'Connection from ip: {request.remote_addr}')

    if file is None:
        logger.warning('File not exists in request')
        return abort(500, 'File not exists in request')

    rnd = randint(1_000_000, 9_999_999)
    rnd_dir = f'dir_archive_{rnd}'

    logger.info(f'Processing {rnd}')

    temp_extracted = temp_dir.joinpath(rnd_dir)
    temp_extracted.mkdir()

    try:
        templates = temp_extracted.absolute()

        archive = zipfile.ZipFile(file)

        if 'index.html' not in archive.namelist():
            return abort(400, 'Index file not found')

        archive.extractall(str(temp_extracted))

        data = process(f'file://{templates}/index.html')

        rmtree(str(temp_extracted))

        if data is None:
            return abort(400, 'Failed to generate pdf (empty data)')

        return Response(data, headers={
            'Content-Type': 'application/pdf',
            'Content-Disposition': 'attachment; filename=html.pdf',
        })
    except Exception as e:
        logger.error(e)

        try:
            rmtree(str(temp_extracted))
        except:
            pass

        return abort(500, 'Internal server error')
