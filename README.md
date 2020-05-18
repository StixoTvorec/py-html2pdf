# py-html2pdf

### Usage:


#### Start server

```bash
python3 -mvenv venv

source venv/bin/activate

pip install -r requirements.txt

gunicorn --bind 127.0.0.1:8082 --threads 4 app:app

# or (for develop)

python debug.py --bind 127.0.0.1:8082 --debug
```

#### Then

```bash
curl -X POST -F "html=@archive.zip" http://127.0.0.1:8082 -o out.pdf
```
