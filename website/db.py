from flask import g

import website.database


def get_db():
    if 'db' not in g:
        g.db = website.database.DynamoDatabase()

    return g.db




def get_se():
    if 'se' not in g:
        g.se = website.database.SelectSearchEngine()

    return g.se


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)