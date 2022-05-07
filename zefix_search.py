from flask import Flask, render_template, request, url_for, flash, redirect, Response
import subprocess
import ndjson

app = Flask(__name__)
app.config['SECRET_KEY'] = '412fd539978690defac7489c12e689dbd85c4c034fa42801'

messages = [{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]

@app.route("/")
def index():
    # return "<h1 style='color:blue'>Hello There!</h1>"
    return render_template('index.html', messages=messages)

@app.route('/create/', methods=('GET',)) #, 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        # content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            # messages.append({'title': title, 'content': content})
            # return redirect(url_for('index'))
            
            process = subprocess.run(['/usr/bin/rg', '--search-zip', '--text', '--fixed-strings', title, '--no-filename', '--no-line-number', '/home/ubuntu/zefix.tar.zst'], capture_output=True, universal_newlines=True)
            nl='\n'
            return Response(f'[{process.stdout.strip().replace(nl, ",")}]', mimetype='application/json')

    return render_template('create.html')

@app.route('/search/')
def search():
    process = subprocess.run(['/usr/bin/rg', '--search-zip', '--text', '--fixed-strings', request.args.get('q'), '--no-filename', '--no-line-number', '/home/ubuntu/zefix.tar.zst'], capture_output=True, universal_newlines=True)
    nl='\n'
    return Response(f'[{process.stdout.strip().replace(nl, ",")}]', mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
