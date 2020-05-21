from app.server import app
from argparse import ArgumentParser

_args = ArgumentParser()
_args.add_argument('-b', '--bind', help='Bind url', default='127.0.0.1:8082')
_args.add_argument('--debug', action='store_true')
args = _args.parse_args()

parsed_url = args.bind.split(':')

assert len(parsed_url) == 2

app.run(*parsed_url, args.debug)
