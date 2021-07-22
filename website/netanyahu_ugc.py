from flask import g

def transform(ugc):
    if not g.netanyahu:
        return ugc

    new_ugc = []
    for u in ugc:
        new_u = {
            'censored': u.get('censored', False),
            'ugcdocid': u['ugcdocid'],
            'pages': u['pages'],
            'summary': u.get('summary', '').strip(),
            'date': u.get('date', '').strip(),
            'title': u.get('title2', u.get('title', '')).strip(),
            'who': u.get('who', '').strip()
        }

        if new_u['summary'] and new_u['summary'][-1] != '.':
            new_u['summary'] = '%s%s' % (new_u['summary'], '.')

        new_ugc.append(new_u)

    def sort_by_date_key(u):
        if u:
            return tuple(u['date'].split('/')[::-1])
        else:
            return ('0000', '00', '00')

    new_ugc.sort(key=sort_by_date_key)

    return new_ugc
