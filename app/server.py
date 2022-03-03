import os
import zipfile
from pathlib import Path
from shutil import rmtree
from yaml import safe_load
import nanoid

from flask import Flask, request, Response, abort
from pyvirtualdisplay import Display
from werkzeug.datastructures import FileStorage

Display().start()

from .meta import version
from .pdf_generator import process
from ._logger import init as init_logger

try:
    with open('config.yml', 'rb') as r:
        config = safe_load(r)
except FileNotFoundError:
    config = {}

logger = init_logger(config.get('log_level', ''), config.get('log_file', ''))

app = Flask('app')
app.debug = bool(os.environ.get("DEBUG"))

temp_dir = Path(__file__).parent.parent.joinpath('var')

for _item in temp_dir.iterdir():
    rmtree(str(_item), ignore_errors=True)

temp_dir.mkdir(exist_ok=True, parents=True)


@app.route('/', methods=['GET'])
def index_page():
    return Response('Not found', status=404)


@app.route('/health', methods=['GET', 'HEAD'])
def health():
    return Response('Ok')


@app.route('/version', methods=['GET'])
def get_version():
    return Response(version)


@app.route('/', methods=['POST'])
def generate():
    file = request.files.get('html', None)  # type: FileStorage

    logger.info(f'Connection from ip: {request.remote_addr}')

    if file is None:
        logger.warning('File not exists in request')
        return abort(400, 'File not exists in request')

    rnd = nanoid.generate(size=6)
    rnd_dir = f'dir_archive_{rnd}'

    logger.info(f'Processing {rnd}')

    temp_extracted = temp_dir.joinpath(rnd_dir)
    temp_extracted.mkdir()

    try:
        templates = temp_extracted.absolute()

        archive = zipfile.ZipFile(file)

        if 'index.html' not in archive.namelist():
            logger.info(f'Failed to generate pdf "{rnd}" (empty data)')
            return abort(400, 'Index file not found')

        archive.extractall(str(temp_extracted))

        data = process(f'file://{templates}/index.html')

        rmtree(str(temp_extracted), ignore_errors=True)

        if data is None:
            logger.info(f'Failed to generate pdf "{rnd}" (empty data)')
            return abort(400, 'Failed to generate pdf (empty data)')

        return Response(data, headers={
            'Content-Type': 'application/pdf',
            'Content-Disposition': 'attachment; filename=html.pdf',
        })
    except Exception as e:
        logger.error(e)

        rmtree(str(temp_extracted), ignore_errors=True)

        return abort(500, 'Internal server error')
