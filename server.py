from flask import Flask, g, request, render_template, abort
import sqlite3
import datetime

# -- leave these lines intact --
app = Flask(__name__)

def get_db():
    if not hasattr(g, 'sqlite_db'):
        db_name = app.config.get('DATABASE', 'squawker.db')
        g.sqlite_db = sqlite3.connect(db_name)

    return g.sqlite_db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'sqlite_db', None)
    if db is not None:
        db.close()
# ------------------------------

@app.route('/', methods = ["GET", "POST"])
def root():
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        newS = request.form["msg"]
        if len(newS) <= 140:
            toExecute="INSERT INTO squawks (squawk) VALUES (?)"
            cur.execute(toExecute, [newS])
            conn.commit()
        else:
            abort(400)
            
            
    sel = "SELECT * FROM squawks ORDER BY ts DESC"
    cur.execute(sel)
    allS = cur.fetchall()
    cur.close()
    return render_template("index.html", squawks=allS)

if __name__ == '__main__':
    app.debug = True
    app.run()
