from flask import Blueprint, jsonify, request

from . import db

import base64
import json

rest_blueprint = Blueprint('rest_blueprint', __name__)


@rest_blueprint.route('/api/1.0/db/get-view', methods=['POST'])


def get_view():
    j = request.json
    print(j)
    return jsonify(db.get_db().get_view(j))


@rest_blueprint.route('/api/1.0/search/search-views', methods=['POST'])
def search_views():
    j = request.json
    type = j['type']
    search_string = j['search_string']
    page = j['page']
    page_size = int(j['page_size'])
    assert page_size == 25
    r = db.get_se().search_views(type, search_string, page, page_size)
    as_list = list(r)
    return jsonify(as_list)