from os import name
from logging import error


if name == 'nt':
    error('Windows OS not supported!')
    exit(1)
