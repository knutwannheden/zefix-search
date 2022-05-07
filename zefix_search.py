import os
import subprocess
import regex

from dotenv import dotenv_values
from flask import Flask, render_template, request, flash, Response

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
        # Poll process.stdout to show stdout live
        while True:
            line = process.stdout.readline()
            if process.poll() is not None:
                break
            if line:
                yield line
        process.poll()

    return app.response_class(generate(), mimetype='binary/octet-stream')
    # return Response(f'[{process.stdout.strip().replace(nl, ",")}]', mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
