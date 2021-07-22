import json
import time

from flask import url_for, render_template, request, abort, Response, redirect, g, jsonify,\
    Blueprint

from flask_login import login_required

from . import hebrew
from . import db
from . import Ugc
from . import netanyahu_ugc
from . import forms

view_blueprint = Blueprint('view_blueprint', __name__)


@view_blueprint.route(f'/echo', methods=['POST', 'GET'])
def echo():
    if request.json:
        return jsonify({'ok': True, 'r': request.json})
    return jsonify({'ok': True})

@view_blueprint.route(f'/{hebrew.ugc_form}/<string:hebrew_type>/<string:viewid>')
@login_required
def ugc_form(hebrew_type, viewid):
    type = hebrew.generic_views_h2e[hebrew_type]
    if type != 'n' or viewid != '67104-01-20':
        abort(404)

    k = {'case_id': {type: viewid}}
    ugc = Ugc().get_ugc_for_view(k)

    return render_template('documents-form.html', ugc=ugc,
                           hebrew_type=hebrew_type, viewid=viewid)

@view_blueprint.route(f'/{hebrew.ugc_form}/<string:hebrew_type>/<string:viewid>/{hebrew.ugc_submit}', methods=['POST'])
@login_required
def ugc_form_submit(hebrew_type, viewid):
    type = hebrew.generic_views_h2e[hebrew_type]
    if type != 'n' or viewid != '67104-01-20':
        abort(404)

    k = {'case_id': {type: viewid}}
    ugcdocid = request.form['ugcdocid']
    Ugc().update_metadata(json.dumps(k), ugcdocid, request.form)
    return jsonify({'ok': True})

@view_blueprint.route(f'/{hebrew.external}')
def external():
    d = dict(request.args)
    n = {}
    h = {}
    for k, v in d.items():
        if k in hebrew.external_h2e:
            v = v[0].replace('_', '/')
            n[hebrew.external_h2e[k]] = v
            h[k] = v

    n['p'] = 0
    database = db.get_db()
    j = database.get_view(n)
    new_e = []
    for case, title in j['data']['elements']:
        new_e.append({'case': case, 'title': title})
    j['data']['elements'] = new_e
    add_links_to_elements(j)
    number = n['CaseDisplayIdentifier']
    name = n['CaseTypeShortName']

    display_name = f'{name} {number}'
    viewname=f'{name} {number}'

    body = render_template('external.html', hebrew_map=h, name=display_name, page=1, model=j['data'],
                           last_page=1, pages=1,
                           cases_count=len(j['data']['elements']), viewname=viewname, og_description=display_name)

    resp = Response(body)
    resp.headers.set('Cache-Control', f'public, max-age={45 * 24 * 3600}')
    return resp

def prepare_linked_cases(j):
    linked_cases = j.get('linked_cases', [])
    for linked_case in linked_cases:
        if linked_case.get('CaseLinkTypeName', '') == 'חיצוני' and linked_case.get('CaseID') is None:
            new = {}
            for k, v in linked_case.items():
                if not v:
                    continue
                k = hebrew.external_e2h[k]
                new[k] = v.replace('/', '_')
            linked_case['url'] = url_for('.external', **new)

@view_blueprint.route(f'/<string:hebrew_type>/<string:viewid>')
def x_case(hebrew_type, viewid):
    if hebrew_type not in hebrew.generic_views_h2e:
        abort(404)
    if viewid == '0-0-0':
        print( 1 /0)
    type = hebrew.generic_views_h2e[hebrew_type]
    database = db.get_db()
    k = {'case_id': {type: viewid}}
    r = database.get_view(k)

    recompute = None
    if 't' in r:
        recompute = hebrew.ymd(r['t'])

    if r.get('data'):
        if 'deleted' in r['data']['data'] and r['data']['data']['deleted'] == True:
            body = render_template('censored.html')
            resp = Response(body)
            resp.headers.set('Cache-Control', f'public, max-age={45 * 24 * 3600}')
            return resp

    if r is None or 'block' in r:
        abort(404)

    ugc = Ugc().get_ugc_for_view(k)
    ugc = netanyahu_ugc.transform(ugc)
    try:
        j = r['from_master']['data']['result']
        title = j['casename']
    except:
        j = r['data']['data']
        title = r['data']['title']

    try:
        title_from_satellite = r['data']['title']
    except:
        title_from_satellite = title

    try:
        contains_censorship = r['data']['data'].get('contains_censorship')
    except:
        contains_censorship = False
    if contains_censorship:
        title = title_from_satellite
        j['parties'] = r['data']['data']['parties']
        j['casename'] = title_from_satellite

    tik_plili = hebrew.tik_plili in j.get('caseTypeID', '')
    seifei_ishum =None
    if tik_plili:
        seifei_ishum = j.get('merged', {}).get('by_date', {}).get('CaseInterestName', None)


    pref = {'t': 't-', 'n': ''}[type]
    short = f'https://tl8.me/{pref}{viewid}'
    if g.netanyahu:
        short = f'https://tl8.me/bb'

    if 'courtID' in j and 'judge' in j:
        og_description_case = hebrew.og_description_case.format(j['courtID'], j['judge'])
        og_description_case = f'{og_description_case}. {j["caseTypeID"]}'
    else:
        og_description_case = 'תיק בית משפט'
    parties = []
    if r.get('from_master', {}).get('data', {}).get('scraped'):
        scraped = r['from_master']['data']['scraped']
        scraped = hebrew.ymd(scraped)
    elif 'scraped' in j and j['scraped']:
        scraped = j['scraped']
        scraped = hebrew.ymd(scraped)
    elif r.get('data', {}).get('data', {}).get('scraped'):
        scraped = r['data']['data']['scraped']
        scraped = hebrew.ymd(scraped)
    else:
        scraped = None
    j['parties_v2'] = []

    prepare_linked_cases(j)

    for p in j['parties']:
        if 'name' in p and 'status' in p:
            parties.append(f'{p["name"]} ({p["status"]})')
        else:
            name = p['FullName']
            status = p['RoleName']
            parties.append(f'{name} ({status}')
            p['represented_by'] = p.get('RepresentatedOrRepresentativesNames', '').split(',')
            p['represented_by'] = [x.strip() for x in p['represented_by']]
            p['name'] = p['FullName']
            j['parties_v2'].append(p)
    og_description_case = f'{og_description_case}. {", ".join(parties)}'

    linked_cases = []
    seen = set()
    for x in j.get('linked_cases', []):
        fields = 'number', 'CaseDisplayIdentifier'
        n = None
        for f in fields:
            if f in x:
                n = x[f]
                break

        if n not in seen and n is not None:
            linked_cases.append(x)
            seen.add(n)

    try:
        from_master_ts = r['from_master']['api']['ts']
        from_master_ts = hebrew.ymd(from_master_ts)
    except:
        from_master_ts = None

    auto_scrap = (from_master_ts != hebrew.ymd(int(time.time())) or from_master_ts is None)

    try:
        if 'dont_scrap' in r['from_master']['permissions']:
            auto_scrap = False
    except:
        pass

    tomorrow = (from_master_ts is not None \
                  and from_master_ts == hebrew.ymd(int(time.time())))

    form = forms.CaseForm()
    form.view_id.data = viewid
    form.case_type.data = type

    j['linked_cases'] = linked_cases
    if r.get('data', {}).get('entities'):
        satellite = r['data']['entities']
    else:
        satellite = {}



    body = render_template('n.html', model=j, hebrew_type=hebrew_type, subtitle=title, viewid=viewid, short=short,
                           tik_plili=tik_plili, seifei_ishum=seifei_ishum, ugc=ugc, eng_type=type,
                           recompute=recompute,
                           from_master_ts=from_master_ts, auto_scrap=auto_scrap, tomorrow=tomorrow, form=form,
                           from_master=r.get('from_master'), contains_censorship=j.get('contains_censorship'),
                           body_harm=[], satellite=satellite, og_description=og_description_case, scraped=scraped)
    resp = Response(body)
    resp.headers.set('Cache-Control', f'public, max-age={45 * 24 * 3600}')
    return resp


@view_blueprint.route(f'/{hebrew.judge}/<path:name>')
def judge(name):
    return entity(name, 'J')


@view_blueprint.route(f'/{hebrew.side_old}/<path:name>')
def side_old(name):
    return redirect(url_for('view_blueprint.side', name=name), 301)


@view_blueprint.route(f'/{hebrew.side}/<path:name>')
def side(name):
    return entity(name, 'S')


@view_blueprint.route(f'/{hebrew.lawyer}/<path:name>')
def lawyer(name):
    return entity(name, 'L')


@view_blueprint.route(f'/{hebrew.pairs}/<path:name1>/<path:name2>')
def pair(name1, name2):
    name1 = name1.replace('%2F', '/')
    name2 = name2.replace('%2F', '/')
    display_name = hebrew.pair_and.format(name1, name2)
    return entity(f'{name1}|{name2}', 'P', display_name=display_name, name1=name1, name2=name2)

@view_blueprint.after_request
def dont_index_paginated(r):
    page = int(request.args.get(hebrew.page, 1))
    if page != 1:
        r.headers['X-Robots-Tag'] = 'noindex'
    return r


def entity(name, type, display_name=None, **kwargs):
    display_name = display_name or name
    page = int(request.args.get(hebrew.page, 1))
    j = get_cases_list(type, name, page)
    last_page = int(j['data']['total'] / j['data']['batch_size']) + 2
    viewname = {'P': 'pair', 'L': 'lawyer', 'S': 'side', 'J': 'judge'}
    viewname = viewname[type]
    viewname = f'{view_blueprint.name}.{viewname}'

    r1 = range(1, min(10, last_page))
    r2 = range(max(1, page-5), min(page+5, last_page))
    r3 = range(max(1, last_page-10), last_page)

    ranges = r1, r2, r3

    pages = []
    max_seen = None
    for pages_range in ranges:
        for page_no in pages_range:
            if max_seen is None or page_no > max_seen:
                max_seen = page_no
            elif page_no < max_seen:
                continue

            if page_no in pages:
                continue
            elif page_no != 1 and page_no-1 not in pages:
                pages.extend(('...', page_no))
            else:
                pages.append(page_no)

    body = render_template('entity.html', type=type, name=display_name, page=page, model=j['data'],
                           last_page=last_page, pages=pages, subtitle=display_name,
                           cases_count=len(j['data']['elements']), viewname=viewname, og_description=display_name,
                           **kwargs)

    resp = Response(body)
    resp.headers.set('Cache-Control', f'public, max-age={45 * 24 * 3600}')
    return resp

def get_cases_list(type, name, page):
    database = db.get_db()
    j = database.get_view({'t': type, 'n': name, 'p': page - 1})
    return add_links_to_elements(j)

def add_links_to_elements(j):
    for c in j['data']['elements']:
        case = c['case']
        parts = case.split(':')
        hebrew_type = hebrew.generic_views_e2h[parts[0]]
        url = url_for('view_blueprint.x_case', hebrew_type=hebrew_type, viewid=parts[1])
        c['url'] = url
    return j


@view_blueprint.route('/')
def main():
    if g.netanyahu:
        return redirect(url_for('view_blueprint.x_case', hebrew_type=hebrew.case, viewid='67104-01-20'))
    else:
        return redirect(url_for('static_blueprint.search'))


@view_blueprint.route('/delete', methods=['POST'])
def delete():
    form = forms.CaseForm()
    case_type = form.data['case_type']
    viewid = form.data['view_id']
    hebrew_type = hebrew.generic_views_e2h[case_type]
    source_url = url_for('view_blueprint.x_case', hebrew_type=hebrew_type, viewid=viewid)
    if not form.validate_on_submit():
        return redirect(source_url)

    from tolaatcom_nhc.one_case import OneCase

    oc = OneCase()
    key = {'case_id': {'S': f'{case_type}:{viewid}'}}
    oc.set_permissions(key, 'deleted', 'has_censorship')
    oc.set_permissions(key, 'dont_scrap', 'censored')
    
    return redirect(source_url)