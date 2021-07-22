from flask import Blueprint, jsonify, url_for

from . import hebrew
from . import db
from . import database_common

search_blueprint = Blueprint('search_blueprint', __name__)


@search_blueprint.route('/search-query/case/<string:q>/<int:page>')
def search_query(q, page):
    if not q:
        return jsonify({'results': []})
    se = db.get_se()
    page_size = 25
    records = se.search_views('case', q, page, page_size=page_size)
    records = list(records)
    has_more = len(records) > page_size
    records = records[:page_size]
    results = []
    for r in records:
        viewtype, viewid = tuple(r['case'].split(':'))
        hebrew_type = hebrew.generic_views_e2h[viewtype]

        result = {'id': r['case'],
             'text': database_common.search_string_highlight(q, r['name']),
             'url': url_for(f'view_blueprint.x_case', hebrew_type=hebrew_type, viewid=viewid)
             }

        results.append(result)

    result_obj = {'results': results, 'pagination': {'more': has_more}, 'q': q}
    j = jsonify(result_obj)
    j.headers.set('Cache-Control', f'public, max-age={7*24*3600}')
    return j


@search_blueprint.route('/search-query/<string:type>/<string:q>/<int:page>')
def search_query_entity(q, page, type):
    if not q:
        return jsonify({'results': []})
    se = db.get_se()
    page_size = 25
    records = se.search_views(type, q, page, page_size=page_size)
    records = list(records)
    has_more = len(records) > page_size
    records = records[:page_size]
    results = []
    types = {'J': 'judge', 'S': 'side', 'L': 'lawyer'}
    for r in records:
        if r['count'] > 1:
            cases = hebrew.n_cases.format(r['count'])
            url = url_for(f'view_blueprint.{types[type]}', name=r['name'])
        else:
            cases = hebrew.one_case
            parts = r['case'].split(':')
            hebrew_type = hebrew.generic_views_e2h[parts[0]]
            url = url_for('view_blueprint.x_case', hebrew_type=hebrew_type, viewid=parts[1])

        result = {'id': r['name'],
                  'text': f"{se.search_string_highlight(q, r['name'])} {cases}",
                  'url': url
                  }

        results.append(result)

    result_obj = {'results': results, 'pagination': {'more': has_more}, 'q': q}
    j = jsonify(result_obj)
    j.headers.set('Cache-Control', f'public, max-age={7 * 24 * 3600}')
    return j