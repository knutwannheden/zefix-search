import os
import subprocess
from pathlib import Path

import regex as re
from dotenv import dotenv_values
from flask import Flask, render_template, request

config = {**dotenv_values(".env"), **os.environ}

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    query = '\\b' + '[^;]{0,30}'.join(
        [re.escape(s.strip('"')) for s in re.findall('(".*?"|[^ ,.;]+)', request.args.get('q'))]) + '\\b'
    process = subprocess.Popen(
        ['rg', '--search-zip', '--text', '--no-filename', '--no-line-number', '--ignore-case',
         query, *[str(p) for p in Path(f'{config["ZEFIX_DIR"]}/../').glob('zefix-*.tar.zst')]], stdout=subprocess.PIPE)

    def generate():
        while process.poll() is None:
            for line in iter(process.stdout.readline, b''):
                yield line

    return app.response_class(generate(), mimetype='plain/text')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
