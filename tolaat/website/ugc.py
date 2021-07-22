import json
import logging
import datetime
import time
import hashlib
import re
import email
from email.header import decode_header
import base64
import tempfile
from os.path import join
import secrets
from flask import current_app


from website.pdf_helper import count_pages


import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger('ugc.email')

def send_admin_email(subject, html):

    session = boto3.Session()
    ses = session.client('ses', region_name='us-east-1')

    logger.info('send_admin_email: %s, %s', subject, email)

    subject_prefix ='תולעת'
    subject = f'{subject_prefix}: {subject}'

    emails = ['andyworms@gmail.com', 'zo.merg@gmail.com']
    ses.send_email(Source='x@tl8.me',
                   Destination={'ToAddresses': emails},
                   Message={'Subject': {'Data': subject, 'Charset': 'utf-8'},
                            'Body': {'Html': {'Data': html, 'Charset': 'utf-8'}}})



def hash_file(f):
    bug_size = 65536  # lets read stuff in 64kb chunks!

    sha1algo = hashlib.sha1()
    sha1algo.update(b'tolat mishpat ugc jqQGvOUnzyufgTrEUVaj')

    with open(f, 'rb') as f:
        while True:
            data = f.read(bug_size)
            if not data:
                break
            sha1algo.update(data)

    return sha1algo.hexdigest()


class Ugc:

    def __init__(self):

        self.region = 'eu-central-1' #current_app.config['DEFAULT_REGION']

        self.session = boto3.Session(region_name=self.region)
        self.dynamodb = self.session.client('dynamodb')
        self.s3 = self.session.client('s3')

        self.tablename = 'ugc' #current_app.config['UGC_TABLE']
        self.bucket = 'eu-central-1-ugc'#current_app.config['UGC_BUCKET']
        self.prefix = 'ugc' #current_app.config['UGC_PREFIX']
        self.logger = logging.getLogger('ugc')

    def get_doc_id(self):
        try:
            r = self.dynamodb.update_item(TableName=self.tablename,
                                      Key={'u': {'S': 'counter'}},
                                      UpdateExpression='SET #n=#n+:one',
                                      ExpressionAttributeNames={'#n': 'n'},
                                      ExpressionAttributeValues = {':one': {'N': '1'}},
                                      ReturnValues='UPDATED_NEW')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                self.dynamodb.put_item(TableName=self.tablename,
                                              Item={'u': {'S': 'counter'}, 'n': {'N': '0'}})
                return self.get_doc_id()
        return r['Attributes']['n']['N']

    def lock(self, digid):
        lock = json.dumps({'lock': digid})
        self.dynamodb.put_item(TableName=self.tablename, Item={'u': {'S': lock}})

    def is_locked(self, digid):
        lock = json.dumps({'lock': digid})
        r = self.dynamodb.get_item(TableName=self.tablename, Key={'u': {'S': lock}})
        return 'Item' in r

    def parse_subject(self, subject):
        metik = 'מתיק'
        match = re.match(f'(.*) {metik} ([-0-9]+), (.*)', subject)
        title = match.group(1)
        case = match.group(2)
        name = match.group(3)
        return title, case, name

    def add(self, path, subject, source, hidden):
        dig = hash_file(path)

        if self.is_locked(dig):
            self.logger.info('%s is locked', dig)
            return None

        key = {'doc-sha1': dig}
        key = json.dumps(key)

        n = datetime.date.today().strftime('%Y/%m/%d')
        s3path = f'{self.prefix}{n}{dig}.pdf'
        self.s3.upload_file(Filename=path, Bucket=self.bucket, Key=s3path, ExtraArgs={'ContentType': 'application/pdf'})
        num_pages = count_pages(path)
        ugcdocid = self.get_doc_id()
        item = {'u': {'S': key}, 'ugcdocid': {'N': ugcdocid}}
        logging.info('Adding document %s', key)
        self.dynamodb.put_item(TableName=self.tablename, Item=item)

        if subject is not None:
            title, case, name = self.parse_subject(subject)
            k = json.dumps({'case_id': {'n': case}})
        else:
            k = key
            title = 'מסמך' + ' ' + str(ugcdocid)

        key = str(secrets.randbelow(10**8))

        d = datetime.date.fromtimestamp(int(time.time())).strftime("%d/%m/%Y")
        metadata = {'M': {'title': {'S': title},
                          'uploaded': {'S': d},
                          'key': {'S': key},
                          'pages': {'N': str(num_pages)},
                          'original': {'BOOL': 'original_copy' in path},
                          's3path': {'S': s3path},
                          'ugcdocid': {'S': ugcdocid},
                          'source': {'S': source}}}

        if hidden:
            metadata['M']['censored'] = {'BOOL': True}
        try:
            self.dynamodb.update_item(TableName=self.tablename,
                                      Key={'u': {'S': k}},
                                      UpdateExpression='SET #contributions = :first',
                                      ExpressionAttributeNames={'#contributions': 'contributions'},
                                      ExpressionAttributeValues={':first': {'M': {ugcdocid:  metadata}}},
                                      ConditionExpression='attribute_not_exists(#contributions)')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                self.logger.info('Already exists, need to add %s', dig)
                self.dynamodb.update_item(TableName=self.tablename,
                                          Key={'u': {'S': k}},
                                          UpdateExpression='SET #contributions.#ugcdocid = :doc',
                                          ExpressionAttributeNames={'#contributions': 'contributions',
                                                                    '#ugcdocid': ugcdocid},
                                          ExpressionAttributeValues={':doc': metadata})
            else:
                raise

        k2 = json.dumps({'ugcdocid': ugcdocid})
        item = {'u': {'S': k2}, 'caseid': {'S': k}, 'dig': {'S': dig}, 's3path': {'S': s3path}}
        self.dynamodb.put_item(TableName=self.tablename, Item=item)
        self.lock(dig)
        return ugcdocid, key

    def _get_ugc_internal(self, view):
        key = json.dumps(view)
        request_items = {self.tablename: {'Keys': [{'u': {'S': key}}]}}
        resp = self.dynamodb.batch_get_item(RequestItems=request_items)
        r = resp['Responses'][self.tablename]
        if not r:
            return []
        else:
            return r[0]

    def update_metadata(self, k, ugcdocid, form):
        r = self.dynamodb.get_item(TableName=self.tablename, Key={'u': {'S': k}})
        metadata = r['Item']['contributions']['M'][ugcdocid]
        for k, v in form.items():
            metadata['M'][k] = {'S': v}

        self.dynamodb.put_item(TableName=self.tablename, Item=r['Item'])

    def update_censorship_status(self, k, ugcdocid, key, pages, censored):
        r = self.dynamodb.get_item(TableName=self.tablename, Key={'u': {'S': json.dumps(k)}})
        metadata = r['Item']['contributions']['M'][f'{ugcdocid}']

        assert key == metadata['M']['key']['S']

        if censored:
            metadata['M']['censored'] = {'BOOL': censored}
        else:
            if 'censored' in metadata['M']:
                del metadata['M']['censored']

        skippages = pages.split(',')
        skippages = [str(int(x.strip())) for x in skippages if x.strip()]
        if skippages:
            metadata['M']['skippages'] = {'NS': skippages}
        else:
            if 'skippages' in metadata['M']:
                del metadata['M']['skippages']
        self.dynamodb.put_item(TableName=self.tablename, Item=r['Item'])


    def get_ugcdocid_record(self, ugcdocid):
        k ={'ugcdocid': ugcdocid}
        return self.get_by_jsonkey(k)

    def get_by_jsonkey(self, jsonkey):
        return self.get_by_strkey(json.dumps(jsonkey))

    def get_by_strkey(self, strkey):
        return self.dynamodb.get_item(TableName=self.tablename, Key={'u': {'S': strkey}})

    def get_ugc_for_view(self, view):
        if current_app.config['SERVER'] == '1':
            return self.get_ugc_for_view_server(view)
        else:
            # for now no user content
            # in client
            return []

    def get_ugc_for_view_server(self, view):
        r = self._get_ugc_internal(view)
        if not r:
            return []
        contributions = r['contributions']['M']
        ugcs = []
        for document, metadata in contributions.items():
            m = {k: next(iter(v.values())) for k, v in metadata['M'].items()}
            ugcs.append(m)

        def sort_key(x):
            parts = x['uploaded'].split('/')[::-1]
            parts.append(x['ugcdocid'])
            return tuple(parts)

        ugcs.sort(key=sort_key)
        return ugcs

    def get_ugc_for_view_and_ugcdocid(self, view, ugcdocid):
        r = self._get_ugc_internal(view)
        if not r:
            return None
        contributions = r['contributions']['M']
        metadata = contributions[ugcdocid]
        m = {k: next(iter(v.values())) for k, v in metadata['M'].items()}
        m['document'] = ugcdocid
        return m

    def get_ugc_standalone(self, ugcdocid):
        r = self.get_by_jsonkey({'ugcdocid': ugcdocid})
        if not r or 'Item' not in r:
            return None
        caseid = r['Item']['caseid']['S']
        r2 = self.get_by_strkey(caseid)

        contributions = r2['Item']['contributions']['M']
        metadata = contributions[ugcdocid]
        m = {k: next(iter(v.values())) for k, v in metadata['M'].items()}
        m['document'] = ugcdocid
        return m




class EmailParser:


    def get_headers_as_map(self, e):
        return {h[0]: h[1] for h in e._headers}

    def is_spam(self, headers):

        c1 = headers.get('X-SES-Spam-Verdict') == 'PASS'
        c2 = headers.get('X-SES-Virus-Verdict') == 'PASS'
        c3 = headers.get('Received-SPF').startswith('pass')
        c4 = 'spf=pass' in headers.get('Authentication-Results')

        ok = c1 and c2 and c3 and c4
        return not ok


    def parse(self, source):
        logger.info('incoming source %s', source)

        session = boto3.Session(region_name='us-east-1')
        s3 = session.client('s3')

        workdir = tempfile.mkdtemp()

        local_file = join(workdir, 'email.txt')

        parts = source.split('/')
        bucket = parts[2]
        key = '/'.join(parts[3:])

        s3.download_file(bucket, key, local_file)

        with open(local_file, 'rb') as f:
            e = email.message_from_binary_file(f)
            from_ = e.get('From')

            trusted_senders = 'andyworms@gmail.com', 'zomerg@gmail.com'

            is_trusted = False
            for ts in trusted_senders:
                if ts == from_.strip():
                    is_trusted = True
                    break
                if f'<{ts}>' in from_:
                    is_trusted = True
                    break

            headers = self.get_headers_as_map(e)
            passes_spf = headers.get('Received-SPF').startswith('pass')

            is_trusted = is_trusted and passes_spf

            toaddr = e.get('To')
            logger.info('incoming from %s to %s', from_, toaddr)
            hidden = False
            if toaddr=='<hide@tl8.me>':
                hidden = True

            accepted_to = '67104', 'document'
            accepted_to = [f'{t}@tl8.me' for t in accepted_to]
            accepted_to += [f'<{t}>' for t in accepted_to]

            if from_ != '<NetHamishpat@court.gov.il>' and toaddr not in accepted_to:
                import html
                send_admin_email('אימייל נדחה', f' הגיע מכתובת לא מוכרת: {html.escape(from_)}')
                logger.info('canceled because from is %s', from_)

                return f'Canceled because from is {from_}'

            subject = e.get('Subject')

            subject = decode_header(subject)
            if type(subject[0][0]) == str:
                subject = subject[0][0]
            else:
                subject = subject[0][0].decode('utf-8')

            if toaddr == '<67104@tl8.me>' or toaddr == '67104@tl8.me':
                subject = 'מסמך מתיק 67104-01-20, מדינת ישראל נ\' נתניהו ואח\''
                assert is_trusted

            elif toaddr == '<document@tl8.me>' or toaddr == 'document@tl8.me':
                if not subject.strip():
                    subject = None
                else:
                    mism = 'מסמך מתיק'
                    name = 'שם תיק'
                    subject = f'{mism} {subject}, {name}'
                assert is_trusted

            logger.info('subject is %s', subject)

            for part in e.walk():
                ct = part.get_content_type()
                if ct not in ('application/octet-stream', 'application/pdf'):
                    continue
                fn = part.get_filename()
                if not fn.endswith('.pdf'):
                    continue
                pl = part.get_payload()
                filename = part.get_filename()
                decoded = base64.b64decode(pl)
                attachment_path_1 = join(workdir, filename)
                attachment_path_2 = join(workdir, 'local.txt')

                try:
                    with open(attachment_path_1, 'wb') as outf:
                        outf.write(decoded)
                    attachment_path = attachment_path_1
                except:
                    with open(attachment_path_2, 'wb') as outf:
                        outf.write(decoded)
                    attachment_path = attachment_path_2

                ugc = Ugc()
                r = ugc.add(attachment_path, subject, source, hidden)
                if r is None:
                    return
                ugcdocid, key = r

                new_doc='צפיה'
                admin = 'ניהול'
                url = f'https://tl8.me/u-{ugcdocid}'
                admin_url = f'https://tl8.me/u-{ugcdocid}-{key}'
                hidden_msg = ''
                if hidden:
                    hidden_msg = 'מסמך לא מוצג כרגע '
                html= f'{hidden_msg}<a href="{url}">{new_doc}</a> <a href="{admin_url}">{admin}</a>'

                if subject is None:
                    subject = 'מסמך עצמאי'
                send_admin_email(f'מסמך חדש: {subject}', html)
                logger.info('Sucesfully added email')


if __name__ == '__main__':

    if True:
        s = f's3://ses-incoming-xwehyvyd/incoming-submissions-from-net-hamishpat/89ckrqvciaivuqd55tmrr3okca1sa17eu7d4gtg1'
        parts = s.split('/')
        host = parts[2]
        bucket = host.split('.')[0]
        key = '/'.join(parts[3:])
        print(bucket)
        print(key)
        t = f's3://{bucket}/{key}'

        ep = EmailParser()
        ep.parse(t)
        exit(0)

