# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, request, session, g, redirect, url_for, abort, \
    render_template, flash, current_app, jsonify

# create our blueprint :)
bp = Blueprint('flaskr', __name__)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(current_app.config['DATABASE'],timeout=5)
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@bp.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT id, title, text FROM entries ORDER BY id DESC')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@bp.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('INSERT INTO entries (title, text) VALUES (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('flaskr.show_entries'))


@bp.route('/delete/<id>', methods=['get'])
def delete_entry(id):
    db = get_db()
    db.execute('DELETE FROM entries WHERE id = (?)', [id])
    db.commit()
    flash('delete successfully')
    return redirect(url_for('flaskr.show_entries'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if session.get('logged_in') == True:
        return redirect(url_for('flaskr.show_entries'))

    db=get_db()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        record = db.execute('select * from users where username= ?', [username]).fetchone()
        if record is None:
            error = 'user do not exist'
        elif record['password'] != password:
            error = 'password not correct'
        else:
            session['logged_in'] = True
            session['username'] = username
            flash('You were logged in')
            return redirect(url_for('flaskr.show_entries'))
    return render_template('login.html')


@bp.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    error = None
    if request.method == 'POST':
        db=get_db()
        username = request.form['username']
        password = request.form['password']
        try:
            db.execute('insert into users values (?,?)', [username, password])
            db.commit()
        except Exception as e:
            error = "username existed"
            return redirect(url_for('flaskr.login'))
    return render_template('sign_in.html', error=error)


@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('flaskr.show_entries'))
