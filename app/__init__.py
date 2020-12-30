from os import name
from logging import error

from .server import app

__all__ = ['app']


if name == 'nt':
    error('Windows OS not supported!')
    exit(1)
