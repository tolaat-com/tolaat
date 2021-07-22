import json

from flask import current_app, Blueprint, url_for, redirect, flash, render_template
from werkzeug.exceptions import NotFound
import boto3


from . import hebrew
from . import db
from . import forms
scrap_blueprint = Blueprint('scrap_blueprint', __name__)


@scrap_blueprint.route(f'/{hebrew.scrap_request}', methods=['POST'])
def scrap_request():
    form = forms.CaseForm()

    view_id = form.view_id.data
    case_type = form.case_type.data
    hebrew_type = hebrew.generic_views_e2h[case_type]
    url = url_for('view_blueprint.x_case', hebrew_type=hebrew_type, viewid=view_id)

    if not form.validate_on_submit():
        flash(hebrew.failed_capcha)
        return redirect(url)


    database = db.get_db()
    k = {'case_id': {case_type: view_id}}
    r = database.get_view(k)

    data = r.get('data', {}).get('data', {})
    data_from_master = r.get('from_master', {}).get('data', {}).get('result', {})
    #assert 'contains_censorship' not in data
    assert 'delete' not in data
    assert 'delete' not in data_from_master
    assert 'dont_scrap' not in r.get('from_master', {}).get('permissions', {})
    assert 'deleted' not in r.get('from_master', {}).get('permissions', {})

    p = {'CaseDisplayIdentifier': view_id, 'CaseType': case_type}
    from tolaatcom_nhc.one_case import OneCase
    master_table = current_app.config['MASTER_TABLE']

    onecase = OneCase(master_table=master_table)
    onecase.handle(p)

    return redirect(url)


@scrap_blueprint.route(f'/{hebrew.scrap_form}', methods=['GET'])
def scrap_form():
    form = forms.ScrapForm()
    short='https://tl8.me/scrape'
    return render_template('scrap-form.html', form=form, short=short)

@scrap_blueprint.route(f'/{hebrew.scrap_form_submit}', methods=['POST'])
def scrap_form_submit():

    form = forms.ScrapForm()

    case_type = form.case_type.data
    number = str(form.number.data)
    month = str(form.month.data).zfill(2)
    year = str(form.year.data).zfill(2)

    view = f'{number}-{month}-{year}'

    if not form.validate_on_submit():
        return redirect(url_for('scrap_blueprint.scrap_form'))

    bm = 'בית משפט'
    t = 'תעבורה'
    map = {bm: 'court', t: 'transport'}
    m = {"command": "get_one_case", "type": map[case_type], "number": str(number), "month": str(month).zfill(2),
         "year": str(year).zfill(2),
         "force": True}

    session = boto3.Session()
    sqs = session.client('sqs')
    cloudformation = session.client('cloudformation')
    paginator = cloudformation.get_paginator('list_exports')
    queueUrl = None
    for r in paginator.paginate():
        exports = r['Exports']
        for export in exports:
            if export['Name'] == 'tasks-queue-url':
                queueUrl = export['Value']
                break
        if not queueUrl:
            break

    map2 = {bm: 'n', t: 't'}


    database = db.get_db()
    k = {'case_id': {map2[case_type]: view}}
    try:
        r = database.get_view(k)
    except NotFound as e:
        pass

    data = r.get('data', {}).get('data', {})
    data_from_master = r.get('from_master', {}).get('data', {}).get('result', {})
    # assert 'contains_censorship' not in data
    assert 'delete' not in data
    assert 'delete' not in data_from_master
    assert 'dont_scrap' not in r.get('from_master', {}).get('permissions', {})
    assert 'deleted' not in r.get('from_master', {}).get('permissions', {})

    sqs.send_message(QueueUrl=queueUrl, MessageBody=json.dumps(m))

    return redirect(url_for('view_blueprint.main'))
