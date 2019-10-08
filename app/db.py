import sqlite3
import psycopg2
import click
from flask import current_app,g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        """
        g.db=sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory=sqlite3.Row
        """
        # Local DB for development
        g.db=psycopg2.connect(dbname="postgres", user="postgres",password="zkdtc1@lbl",host="localhost",port="5433")
        ## Docker DB
        #g.db=psycopg2.connect(dbname="test", user="test",password="pass",host="db",port="5432")
    return g.db

def close_db(e=None):
    db=g.pop('db',None)
    if db is not None:
        db.close()

def init_db():
    db=get_db()
    cur=db.cursor()
    with current_app.open_resource('schema.sql') as f:
        cur.execute(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    # Clear the existing data and create new tables.
    init_db()
    click.echo('Initialized the db.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
