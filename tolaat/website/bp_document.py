from flask import abort, render_template, make_response, send_file, Blueprint, current_app, redirect, \
    url_for, request
import boto3
from email.utils import formatdate
import json
import tempfile
from . import hebrew
from . import bodily_harm
from . import db
from .common import get_short_prefix
from . import Ugc
from . import pdf_helper

from tolaatcom_nhc.pdf_generator import PdfGenerator

from .forms import CensorshipForm

doc_blueprint = Blueprint('doc_blueprint', __name__)

max_size = 4606567


@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/{hebrew.decision}/<int:decisionnumber>')
def x_document_preview(hebrew_type, viewid, decisionnumber):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    case_type = hebrew.generic_views_h2e[hebrew_type]
    return x_document_preview_internal(viewid, decisionnumber, 'decisions', casetype=case_type)

@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/{hebrew.document}/<string:doctype>/<int:decisionnumber>')
def x_document_preview_v2(hebrew_type, viewid, doctype, decisionnumber):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    if doctype not in hebrew.decision_types_h2e:
        abort(404)

    doctype_e = hebrew.decision_types_h2e[doctype]
    case_type = hebrew.generic_views_h2e[hebrew_type]
    return x_document_preview_internal_v2(viewid, doctype_e, decisionnumber, casetype=case_type)


@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/{hebrew.ugc_url}/<string:ugcdocid>')
def x_ugc_preview(hebrew_type, viewid, ugcdocid):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    case_type = hebrew.generic_views_h2e[hebrew_type]
    return x_ugc_preview_internal(viewid, ugcdocid, casetype=case_type)



@doc_blueprint.route(f'/{hebrew.ugc_url}/<string:ugcdocid>')
def x_ugc_short_url(ugcdocid):
    ugc = Ugc()
    d = ugc.get_ugcdocid_record(ugcdocid)
    if 'Item' not in d:
        abort(404)
    caseid = d['Item']['caseid']['S']
    caseid = json.loads(caseid)
    if 'case_id' in caseid:
        for type, viewid in caseid['case_id'].items():
            break
        hebrew_type = hebrew.generic_views_e2h[type]
        url = url_for('doc_blueprint.x_ugc_preview', hebrew_type=hebrew_type, viewid=viewid, ugcdocid=ugcdocid)
        if 'k' in request.args:
            key = request.args.get('k')
            url = f'{url}?k={key}'
        return redirect(url)
    if 'doc-sha1' in caseid:
        c = ugc.get_by_jsonkey(caseid)
        if 'Item' not in c:
            abort(404)
        elem = c['Item']['contributions']['M'][ugcdocid]['M']
        m = {}
        for k, v in elem.items():
            m[k] = list(v.values())[0]
        short = f'https://tl8.me/u-{ugcdocid}'
        return render_template('document-standalone-ugc.html', m=m, short=short)


@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/{hebrew.ktav_teanot}/<int:decisionnumber>')
def n_kitvei_teanot_preview(hebrew_type, viewid, decisionnumber):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    return x_document_preview_internal(viewid, decisionnumber, 'kitvei_teanot', casetype='n')


def abort_has_new_decisions(r):
    from_master = r.get('from_master', {}).get('api', {})
    if 'decisions' in from_master or 'verdicts' in from_master:
        abort(404)


def x_document_preview_internal(viewid, decisionnumber, type, casetype='n'):
    database = db.get_db()
    r = database.get_view({'case_id': {casetype: viewid}})
    if r['data']['data'].get('deleted'):
        abort(404)
    abort_has_new_decisions(r)

    if bodily_harm.is_bodily_harm(r):
        return render_template('decision-bodily-harm.html')
    if r['data']['data'].get('censor_decisions', False):
        if 'unfit' in r['data']['data']:
            return render_template('censored-decision-unfit.html', model=r['data']['data'])
        else:
            return render_template('censored-decision.html', model=r['data']['data'])

    prefix = get_short_prefix(casetype)
    short = f'https://tl8.me/{prefix}{viewid}-{decisionnumber}'
    decision = r['data']['data'][type][decisionnumber]
    censored = 'censored' in decision

    case_name = r['data']['title']
    doc_hebrew_type = hebrew.document_types_e2h[type]
    case_hebrew_type = hebrew.generic_views_e2h[casetype]
    return render_template('document.html', type=type, casetype=casetype, h_type=doc_hebrew_type,
                           viewid=viewid, censored=censored,
                           decisionnumber=decisionnumber, hebrew_type=case_hebrew_type,
                           decision=decision, case_name=case_name, short=short)


def x_document_preview_internal_v2(viewid, doctype_e, decisionnumber, casetype='n'):
    database = db.get_db()
    r = database.get_view({'case_id': {casetype: viewid}})
    if bodily_harm.is_bodily_harm(r):
        return render_template('decision-bodily-harm.html')
    if r.get('data', {}).get('data', {}).get('censor_decisions', False):
        if 'unfit' in r['data']['data']:
            return render_template('censored-decision-unfit.html', model=r['data']['data'])
        else:
            return render_template('censored-decision.html', model=r['data']['data'])

    if is_document_hidden_v2(doctype_e, decisionnumber, r):
        return render_template('censored-decision-1.html', model=r['data']['data'])

    prefix = get_short_prefix(casetype)
    short = f'https://tl8.me/{prefix}{viewid}-{doctype_e[0]}-{decisionnumber}'
    decision = r['from_master']['api'][doctype_e][decisionnumber-1]
    censored = 'censored' in decision
    heb_decision_type = hebrew.decision_types_e2h[doctype_e]

    try:
        case_name = r['from_master']['data']['result']['casename']
    except:
        case_name = r['data']['title']
    case_hebrew_type = hebrew.generic_views_e2h[casetype]
    scraped = hebrew.ymd(r['from_master']['api']['ts'])
    return render_template('document_v2.html', casetype=casetype, scraped=scraped,
                           heb_decision_type=heb_decision_type,
                           viewid=viewid, censored=censored, doctype_e=doctype_e,
                           decisionnumber=decisionnumber, hebrew_type=case_hebrew_type,
                           decision=decision, case_name=case_name, short=short)


def x_ugc_preview_internal(viewid, ugcdocid, casetype='n'):
    database = db.get_db()
    k = {'case_id': {casetype: viewid}}
    r = database.get_view(k)
    if bodily_harm.is_bodily_harm(r):
        return render_template('decision-bodily-harm.html')
    if r.get('data', {}).get('data', {}).get('censor_decisions', False):
        if 'unfit' in r['data']['data']:
            return render_template('censored-decision-unfit.html', model=r['data']['data'])
        else:
            return render_template('censored-decision.html', model=r['data']['data'])

    document = Ugc().get_ugc_for_view_and_ugcdocid(k, ugcdocid)

    key = request.args.get('k', 'default')
    open = document.get('key', 'actual')

    is_admin = key == open

    form = CensorshipForm()
    skippages = document.get('skippages', [])
    skippages = [f'{i}' for i in skippages]
    skippages.sort()
    form.pages.data=','.join(skippages)
    form.key.data = key
    form.censored.data=document.get('censored', False)


    short = f'https://tl8.me/u-{ugcdocid}'
    censored = 'censored' in document

    try:
        case_name = r['data']['title']
    except:
        case_name = r['from_master']['data']['result']['casename']
    case_hebrew_type = hebrew.generic_views_e2h[casetype]

    import random, sys
    r = random.randint(0, sys.maxsize)
    if is_admin:
        template = 'document-ugc-admin.html'
    else:
        template = 'document-ugc.html'

    return render_template(template, type=type, casetype=casetype, is_admin=is_admin,
                           viewid=viewid, censored=censored, ugc=document, form=form,
                           ugcdocid=ugcdocid, hebrew_type=case_hebrew_type, k=key, r=r,
                           case_name=case_name, short=short)


@doc_blueprint.route(f'/submit-admin-ugc/<string:casetype>/<string:viewid>:<int:ugcdocid>', methods=['POST'])
def submit_admin_ugc(viewid, ugcdocid, casetype='n'):
    form = CensorshipForm()
    assert form.validate_on_submit()

    k = {'case_id': {casetype: viewid}}
    key = form.key.data
    pages = form.pages.data
    censored = form.censored.data

    Ugc().update_censorship_status(k, ugcdocid, key, pages, censored)

    ht = hebrew.generic_views_e2h[casetype]
    u = url_for('doc_blueprint.x_ugc_preview', hebrew_type=ht, viewid=viewid, ugcdocid=ugcdocid)
    return redirect(f'{u}?k={key}')

@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/<string:document_type>/<int:decisionnumber>/{hebrew.download}')
def x_document_download(hebrew_type, viewid, decisionnumber, document_type):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    casetype = hebrew.generic_views_h2e[hebrew_type]
    assert document_type in hebrew.document_types_h2e
    response = x_document(hebrew_type, viewid, decisionnumber, document_type)
    casen = "-".join(viewid.split('-')[::-1])
    prefix = get_short_prefix(casetype)
    name = f"{prefix}{hebrew.website_name}-{casen}-{document_type}-{decisionnumber}"
    name = name.replace(' ', '-')
    from urllib.parse import quote
    response.headers.set('Content-Disposition', f'attachment; filename="{quote(name)}.pdf"')
    return response


@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/<string:document_type>/<int:decisionnumber>/{hebrew.view}')
def x_document(hebrew_type, viewid, decisionnumber, document_type):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    casetype = hebrew.generic_views_h2e[hebrew_type]
    bucket = current_app.config['DOCUMENTS_BUCKET']
    region = current_app.config['DEFAULT_REGION']
    prefix = current_app.config['DOCUMENTS_PREFIX']
    document_type_e = hebrew.document_types_h2e[document_type]
    suffix = {'decisions': '', 'kitvei_teanot': '-kt'}[document_type_e]

    s3 = boto3.client('s3', region_name=region)
    database = db.get_db()
    r = database.get_view({'case_id': {casetype: viewid}})
    abort_has_new_decisions(r)
    if bodily_harm.is_bodily_harm(r) or r['data']['data'].get('censor_decisions', False):
        return abort(403)

    if r['data']['data'].get('deleted'):
        return abort(404)

    decision = r['data']['data']['decisions'][decisionnumber]
    if 'censored' in decision:
        return abort(403)

    eng = hebrew.generic_views_h2e[hebrew.case]
    viewid = '-'.join(viewid.split('-')[::-1])
    case_type_prefix = {'n': '', 't': 't/'}[casetype]
    key = f'{prefix}/{case_type_prefix}{eng}-{viewid}{suffix},{decisionnumber}.pdf.gz'
    s3obj = s3.get_object(Bucket=bucket, Key=key)
    r = make_response(send_file(s3obj['Body'], cache_timeout=180 * 24 * 3600, mimetype='application/pdf'))
    r.headers.set('Content-Encoding', 'gzip')
    r.headers.set('ETag', s3obj['ETag'])
    r.headers.set('Last-Modified', formatdate(float(s3obj['LastModified'].timestamp())))
    return r


@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/{hebrew.ugc_url}/<string:ugcdocid>/{hebrew.download}')
def x_ugc_download(hebrew_type, viewid, ugcdocid):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    casetype = hebrew.generic_views_h2e[hebrew_type]
    response = x_ugc(hebrew_type, viewid, ugcdocid)
    casen = "-".join(viewid.split('-')[::-1])
    prefix = get_short_prefix(casetype)
    k = {'case_id': {casetype: viewid}}
    ugc = Ugc().get_ugc_for_view_and_ugcdocid(k, ugcdocid)
    name = f"{prefix}{hebrew.website_name}-{casen}-{hebrew.ugc_url}-{ugc['ugcdocid']}-{ugc['title']}"
    name = name.replace(' ', '-')
    from urllib.parse import quote
    response.headers.set('Content-Disposition', f'attachment; filename="{quote(name)}.pdf"')
    return response


@doc_blueprint.route(f'/{hebrew.ugc_url}/<string:ugcdocid>/{hebrew.download}')
def x_ugc_standalone_download(ugcdocid):
    response = x_ugc_standalone(ugcdocid)
    ugc = Ugc().get_ugc_standalone(ugcdocid)
    title = ugc['title'].replace(' ', '-')
    name = f"{hebrew.website_name}-{hebrew.ugc_url}-{ugc['ugcdocid']}-{title}"
    name = name.replace(' ', '-')
    from urllib.parse import quote
    response.headers.set('Content-Disposition', f'attachment; filename="{quote(name)}.pdf"')
    return response



@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/{hebrew.ugc_url}/<string:ugcdocid>/{hebrew.view}')
def x_ugc(hebrew_type, viewid, ugcdocid):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    casetype = hebrew.generic_views_h2e[hebrew_type]
    bucket = current_app.config['UGC_BUCKET']
    region = current_app.config['DEFAULT_REGION']

    key = request.args.get('k', '-1')

    s3 = boto3.client('s3', region_name=region)
    database = db.get_db()
    k = {'case_id': {casetype: viewid}}
    r = database.get_view(k)
    if bodily_harm.is_bodily_harm(r) or r.get('data', {}).get('data', {}).get('censor_decisions', False):
        return abort(403)

    ugc = Ugc().get_ugc_for_view_and_ugcdocid(k, ugcdocid)
    if 'censored' in ugc:
        if key != ugc.get('key'):
            abort(401)
    key = ugc['s3path']
    s3obj = s3.get_object(Bucket=bucket, Key=key)
    if key.endswith('.gz'):
        f = s3obj['Body']
        from_s3 = tempfile.SpooledTemporaryFile()
        from_s3.write(f.read())
        from_s3.seek(0)
        r = make_response(send_file(from_s3, mimetype='application/pdf'))
        r.headers.set('Content-Encoding', 'gzip')
        return r
    else:
        from_s3 = tempfile.SpooledTemporaryFile()
        b = s3obj['Body'].read()
        size = len(b)
        from_s3.write(b)
        from_s3.seek(0)

        from_s3 = pdf_helper.censor_pages(from_s3, ugc.get('skippages', []))

        if size < max_size:
            r = make_response(send_file(from_s3, cache_timeout=180 * 24 * 3600 - 1, mimetype='application/pdf'))
            r.headers.set('ETag', s3obj['ETag'])
            r.headers.set('Last-Modified', formatdate(float(s3obj['LastModified'].timestamp())))
            return r

        new_key = f'ugc/{viewid}/{ugcdocid}.pdf'
        r = s3.copy_object(ACL='public-read', Bucket='tolaatmish', CopySource={'Bucket': bucket, 'Key': key},
                           Key=new_key, ContentType='application/pdf')

        full_url = f'https://tolaatmish.s3.eu-central-1.amazonaws.com/{new_key}'
        return redirect(full_url)

@doc_blueprint.route(f'/{hebrew.ugc_url}/<string:ugcdocid>/{hebrew.view}')
def x_ugc_standalone(ugcdocid):

    bucket = current_app.config['UGC_BUCKET']
    region = current_app.config['DEFAULT_REGION']

    key = request.args.get('k', '-1')

    s3 = boto3.client('s3', region_name=region)

    ugc = Ugc().get_ugc_standalone(ugcdocid)
    if 'censored' in ugc:
        if key != ugc.get('key'):
            abort(401)
    key = ugc['s3path']
    s3obj = s3.get_object(Bucket=bucket, Key=key)
    if key.endswith('.gz'):
        f = s3obj['Body']
        from_s3 = tempfile.SpooledTemporaryFile()
        from_s3.write(f.read())
        from_s3.seek(0)
        r = make_response(send_file(from_s3, mimetype='application/pdf'))
        r.headers.set('Content-Encoding', 'gzip')
        return r
    else:
        from_s3 = tempfile.SpooledTemporaryFile()
        b = s3obj['Body'].read()
        size = len(b)
        from_s3.write(b)
        from_s3.seek(0)

        from_s3 = pdf_helper.censor_pages(from_s3, ugc.get('skippages', []))

        if size < max_size:
            r = make_response(send_file(from_s3, cache_timeout=180 * 24 * 3600 - 1, mimetype='application/pdf'))
            r.headers.set('ETag', s3obj['ETag'])
            r.headers.set('Last-Modified', formatdate(float(s3obj['LastModified'].timestamp())))
            return r

        new_key = f'ugc/standalone/{ugcdocid}.pdf'
        r = s3.copy_object(ACL='public-read', Bucket='tolaatmish', CopySource={'Bucket': bucket, 'Key': key},
                           Key=new_key, ContentType='application/pdf')

        full_url = f'https://tolaatmish.s3.eu-central-1.amazonaws.com/{new_key}'
        return redirect(full_url)

def is_document_hidden_v2(doc_type, decisionnumber, r):
    hidden = []
    try:
        hidden = r['from_master']['permissions']['hide']
    except:
        pass
    flag = f'{doc_type[0]}:{decisionnumber}'
    return flag in hidden or '*' in hidden


@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/{hebrew.document}/<string:heb_decision_type>/<int:decisionnumber>/{hebrew.view_document}')
def x_document_v2(hebrew_type, viewid, heb_decision_type, decisionnumber):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    if heb_decision_type not in hebrew.decision_types_h2e:
        abort(404)

    casetype = hebrew.generic_views_h2e[hebrew_type]

    database = db.get_db()
    r = database.get_view({'case_id': {casetype: viewid}})

    if bodily_harm.is_bodily_harm(r) or r.get('data', {}).get('data', {}).get('censor_decisions', False):
        return abort(403)

    caseid = r['from_master']['api']['case']['CaseID']

    eng_dec_type = hebrew.decision_types_h2e[heb_decision_type]

    if is_document_hidden_v2(eng_dec_type, decisionnumber, r):
        abort(403)

    pdfg = PdfGenerator()
    p, last_modified = pdfg.build_document(caseid, eng_dec_type, decisionnumber-1)

    p.seek(0, 2) # goto end
    file_size = p.tell()
    p.seek(0)

    if file_size > max_size:
        new_key = f'{casetype}/{viewid}/{eng_dec_type}-{decisionnumber}.pdf'
        s3 = boto3.client('s3')
        bytes = p.read()
        r = s3.put_object(ACL='public-read', Bucket='tolaatmish', Body=bytes, ContentEncoding='gzip',
                           Key=new_key, ContentType='application/pdf')

        full_url = f'https://tolaatmish.s3.eu-central-1.amazonaws.com/{new_key}'
        return redirect(full_url)

    r = make_response(send_file(p, cache_timeout=180 * 24 * 3600 - 1, mimetype='application/pdf'))
    return r


@doc_blueprint.route(f'/<string:hebrew_type>/<string:viewid>/{hebrew.document}/<string:heb_decision_type>/<int:decisionnumber>/{hebrew.download}')
def x_document_v2_download(hebrew_type, viewid, heb_decision_type, decisionnumber):
    response = x_document_v2(hebrew_type, viewid, heb_decision_type, decisionnumber)

    casetype = hebrew.generic_views_h2e[hebrew_type]

    casen = "-".join(viewid.split('-')[::-1])
    prefix = get_short_prefix(casetype)
    name = f"{prefix}{hebrew.website_name}-{casen}-{heb_decision_type}-{decisionnumber}"
    name = name.replace(' ', '-')
    from urllib.parse import quote
    response.headers.set('Content-Disposition', f'attachment; filename="{quote(name)}.pdf"')
    return response
