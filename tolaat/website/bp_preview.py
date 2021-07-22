from flask import abort, render_template, make_response, send_file, Blueprint
from . import hebrew
from tolaatcom_nhc import nethamishpat



preview_blueprint = Blueprint('preview_blueprint', __name__)


def get_case_preview(hebrew_type, viewid):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    type = hebrew.generic_views_h2e[hebrew_type]
    numerator = {'t': '2', 'n': '1'}[type]
    long_type = {'t': 'transport', 'n': 'court'}

    client = nethamishpat.NethamishpatApiClient()
    number, month, year = viewid.split('-')
    c = client.get_by_case(number, month, year, numerator)

    if c is None:
        abort(404)
    if 'd' in c and c['d'].get('CaseID', 0) == 0:
        abort(404)

    c['d']['type'] = long_type[type]
    c['d']['sittings'] = client.get_sittings(c)
    c['d']['verdicts'] = client.get_verdicts(c)
    c['d']['decisions'] = client.get_decisions(c)

    return c, client


@preview_blueprint.route(f'/{hebrew.preview_name}-<string:hebrew_type>/<string:viewid>')
def case_preview(hebrew_type, viewid):
    c, client = get_case_preview(hebrew_type, viewid)
    casetype = hebrew.generic_views_h2e[hebrew_type]
    pref = {'t': 't-', 'n': ''}[casetype]
    short = f'https://tl8.me/d-{pref}{viewid}'
    return render_template('preview-n.html', case=c['d'], hebrew_type=hebrew_type, viewid=viewid, short=short)


@preview_blueprint.route(f'/{hebrew.preview_name}-<string:hebrew_type>/<string:viewid>/<string:hebrew_document_type>/<int:number>')
def original_copy_document(hebrew_type, viewid, hebrew_document_type, number):
    c, client = get_case_preview(hebrew_type, viewid)
    if c is None:
        abort(404)
    m = {hebrew.preview_decision: 'decisions', hebrew.preview_verdict: 'verdicts'}
    document_type = m[hebrew_document_type]
    pdf = client.get_pdf(c['d'][document_type][::-1][number]['DocumentID'])
    pdf.seek(0)
    r = make_response(send_file(pdf, mimetype='application/pdf'))
    return r
