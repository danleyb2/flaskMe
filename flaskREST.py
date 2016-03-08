import json

from flask import Flask, jsonify, g, redirect, abort, request
import sqlite3
import os

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskCars.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = dict_factory  # sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    print("Initializing DB")
    init_db()
    print("Initialized DB")


app.config.from_envvar('FLASKCAR_SETTINGS', silent=True)


@app.route('/')
def hello_world():
    return 'Flask Restfull Sample App'


@app.route('/cars', methods=['GET', 'POST'])
def all_cars():
    db = get_db()
    if request.method == 'POST':
        if request.form.get('name', False) and request.form.get('color', False):
            data = dict(
                name=request.form.get('name'),
                color=request.form.get('color')
            )
        elif request.get_json().get('name',False):#request.headers.get('Content-Type') == 'application/json'
            data = request.get_json()
        else:
            abort(410)

        name = data.get('name')
        color = data.get('color')

        db.execute('INSERT INTO cars (name, color) VALUES (?,?)', [name, color])
        db.commit()
        return jsonify(
            dict(
                name=name,
                color=color
            )
        )
    else:
        cur = db.execute('SELECT id,name,color FROM cars ORDER BY id ASC ')
        entries = cur.fetchall()
        return jsonify(entries)


@app.route('/car/<int:id>')
def car(id):
    db = get_db()
    cur = db.execute('SELECT id,name,color FROM cars WHERE id=?', [id])
    entry = cur.fetchone()
    return jsonify(entry)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    app.debug = True
    app.run()
