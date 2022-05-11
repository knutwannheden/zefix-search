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
    query = '\\b' + '\\b[^;]{0,30}\\b'.join(
        [re.escape(s.strip('"'), literal_spaces=True) for s in re.findall('(".*?"|[^ ,.;]+)', request.args.get('q'))]) + '\\b'
    process = subprocess.Popen(
        ['rg', '--search-zip', '--text', '--no-filename', '--no-line-number', '--ignore-case',
         query, *[str(p) for p in Path(f'{config["ZEFIX_DIR"]}/../').glob('zefix-*.tar.zst')]], stdout=subprocess.PIPE)

    def generate():
        try:
            count = 0
            while process.poll() is None:
                for line in iter(process.stdout.readline, b''):
                    yield line
                    count += 1
                    if count == 5000:
                        yield '...\n'
                        return
        finally:
            print('done')
            process.terminate()

    return app.response_class(generate(), mimetype='plain/text')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
