import json
import os
import sqlite3
import subprocess
from pathlib import Path

import regex as re
from dotenv import dotenv_values
from flask import Flask, render_template, request

config = {**dotenv_values(".env"), **os.environ}
conn = sqlite3.connect(config["DB_FILE"], check_same_thread=False)

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
            process.terminate()

    return app.response_class(generate(), mimetype='plain/text')


@app.route('/search2')
def search2():
    query = "NEAR(" + ' '.join([re.escape(s.strip('"'), literal_spaces=True) for s in re.findall('(".*?"|[^ ,.;]+)', request.args.get('q'))]) + ", 6)"
    print(query)

    def generate():
        cur = conn.cursor()
        try:
            cur.execute('select company_name, company_ehraid, company_chid, publ_date, publ_id, publ_message from zefix where publ_message match ?', (query,))
            count = 0
            while True:
                result = cur.fetchmany(100)
                if not result:
                    return
                else:
                    for row in result:
                        yield f'{{"sogcPublication":{{"sogcId":{row[4]}, "sogcDate":"{row[3]}", "message":{json.dumps(row[5])}}}, "companyShort":{{"name":{json.dumps(row[0])},"ehraid":{json.dumps(row[1])},"chid":{json.dumps(row[2])}}}}}\n'
                        count += 1
                        if count == 5000:
                            yield '...\n'
                            return
        finally:
            cur.close()

    return app.response_class(generate(), mimetype='plain/text')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
