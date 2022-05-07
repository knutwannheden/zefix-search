import os
import subprocess

import regex
from dotenv import dotenv_values
from flask import Flask, render_template, request

config = {**dotenv_values(".env"), **os.environ}

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    query = '\\b' + '[^;]{0,20}'.join(regex.split('[\\s,.;]+', request.args.get('q'))) + '\\b'
    process = subprocess.Popen(
        ['rg', '--search-zip', '--text', '--no-filename', '--no-line-number', query,
         f'{config["ZEFIX_DIR"]}/../zefix.tar.zst'], stdout=subprocess.PIPE)

    def generate():
        while process.poll() is None:
            for line in iter(process.stdout.readline, b''):
                yield line

    return app.response_class(generate(), mimetype='plain/text')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
