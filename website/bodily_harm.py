from . import hebrew

import re

def censor_case_title_dynamo(r):
    title = r['title']['S']
    if ':' not in title or hebrew.against not in title:
        t = r['case_id']['S'].split(':')[1]
        title = f'{t}: {hebrew.anonymized}'
    else:
        ind0 = title.index(':')
        ind1 = title.index(hebrew.against)

        last_part = title[ind1+len(hebrew.against):]
        title = f'{title[:ind0]}: {hebrew.anonymized} {hebrew.against} {last_part}'
    return title

def censor_case_title(r):
    title = r['data']['title']
    if ':' not in title or hebrew.against not in title:
        t = r['case_id']['S'].split(':')[1]
        title = f'{t}: {hebrew.anonymized}'
    else:
        ind0 = title.index(':')
        ind1 = title.index(hebrew.against)

        last_part = title[ind1+len(hebrew.against):]
        title = f'{title[:ind0]}: {hebrew.anonymized} {hebrew.against} {last_part}'
    r['title'] = title
    r['data']['data']['casename'] = title

def is_bodily_harm_dynamo_record(r):
    if 'caseInterestID' in r['data']['B']:
        bodily_harm = is_case_interest_bodily_harm(r['data']['B']['caseInterestID'])
        if not bodily_harm:
            return False

        for p in r['data']['B'].get('parties', []):
            if re.match(hebrew.plaintiff_re, p['status']) and p['name'] != hebrew.anonimous:
                return True



def is_case_interest_bodily_harm(caseInterest):
    return any((h in caseInterest for h in hebrew.bodily_harm))

def is_bodily_harm(r):
    censored_names = set()
    try:
        body = r['from_master']['data']['result']
    except:
        body = r['data']['data']
    if 'caseInterestID' not in body:
        return False
    interest = body['caseInterestID']
    if not is_case_interest_bodily_harm(interest):
        return False

    if 'parties' not in body:
        return False

    has_plaintiff_name = False
    for p in r['data']['data']['parties']:
        if re.match(hebrew.plaintiff_re, p['status']) and p['name'] != hebrew.anonimous:
            has_plaintiff_name = True
            censored_names.add(p['name'])
            p['anon'] = True

    for p in r['data']['data']['parties']:
        if p['name'] in censored_names:
            p['name'] = hebrew.anonymized
            p['anon'] = True

    if has_plaintiff_name:
        censor_case_title(r)

    return has_plaintiff_name