# py-html2pdf

## Installation

```bash
python3 -mvenv venv

source venv/bin/activate

pip install -r requirements.txt
```

## Use as server:


#### Start

```bash
gunicorn --bind 127.0.0.1:8082 --threads 4 app.server:app

# or (for develop)

python debug.py --bind 127.0.0.1:8082 --debug
```

#### Then

```bash
curl -X POST -F "html=@archive.zip" http://127.0.0.1:8082 -o out.pdf
```


## Use as cli converter:

```bash
pip install tqdm  # optional for progress bar

python cli.py path/page-one.html path/page-two.html [...]

# OR

python cli.py --input templates-list.txt  # read from file. Each line as html page

# See help:

python cli.py --help
```
