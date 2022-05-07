import os
import subprocess

from dotenv import dotenv_values
from flask import Flask, render_template, request, flash, Response

config = {**dotenv_values(".env"), **os.environ}

app = Flask(__name__)

messages = [{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]


@app.route("/")
def index():
    # return "<h1 style='color:blue'>Hello There!</h1>"
    return render_template('index.html', messages=messages)


@app.route('/create/', methods=('GET',))  # , 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        # content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            # messages.append({'title': title, 'content': content})
            # return redirect(url_for('index'))

            process = subprocess.run(['rg', '--search-zip', '--text', '--fixed-strings', title, '--no-filename', '--no-line-number',
                                      f'{config["ZEFIX_DIR"]}/../zefix.tar.zst'], capture_output=True, universal_newlines=True)
            nl = '\n'
            return Response(f'[{process.stdout.strip().replace(nl, ",")}]', mimetype='application/json')

    return render_template('search.html')


@app.route('/search/')
def search():
    process = subprocess.run(
        ['rg', '--search-zip', '--text', '--fixed-strings', request.args.get('q'), '--no-filename', '--no-line-number',
         f'{config["ZEFIX_DIR"]}/../zefix.tar.zst'], capture_output=True, universal_newlines=True)
    nl = '\n'
    return Response(f'[{process.stdout.strip().replace(nl, ",")}]', mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
