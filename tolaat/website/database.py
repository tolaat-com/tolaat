from flask import current_app

from website import database_server
from website import database_client


def is_server():
    return current_app.config['SERVER'] == '1'


def get_module():
    if is_server():
        return database_server
    else:
        return database_client


def DynamoDatabase():
    return get_module().DynamoDatabase()


def SelectSearchEngine():
    return get_module().SelectSearchEngine()

