import logging

import email
from email.header import decode_header
from os.path import join
import tempfile


import boto3

logger = logging.getLogger('incoming_email.email')

class Users:

    def __init__(self):
        self.tablename = 'users'
        self.dynamodb = boto3.Session().client('dynamodb')

    def add_subscription(self, email, subscription):
        self.dynamodb.update_item(TableName=self.tablename,
                                  Key={'u': {'S': email}},
                                  UpdateExpression='ADD #s :s',
                                  ExpressionAttributeNames={'#s': 'subscriptions'},
                                  ExpressionAttributeValues={':s': {'SS': [subscription]}}
                                  )

class EmailParser:


    def open(self, email_map):
        session = boto3.Session(region_name='us-east-1')
        ses = session.client('ses')
        email = email_map['from_addr']
        r = ses.verify_email_identity(EmailAddress=email)
        return

    def class_action(self, email_map):
        pass

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
            to = e.get('To')
            logger.info('incoming from %s to %s', from_, to)

            headers = self.get_headers_as_map(e)
            if self.is_spam(headers):
                logger.info('canceled because did not pass spam')
                return 'did not pass spam'
            else:
                logger.info('passed spam')

            message_id = headers['Message-ID']

            subject = e.get('Subject')

            subject = decode_header(subject)
            if type(subject[0][0]) == str:
                subject = subject[0][0]
            else:
                subject = subject[0][0].decode('utf-8')

            if '<' in from_ and '>' in from_:
                from_name = from_[:from_.index('<')-1]
                from_addr = from_[from_.index('<')+1:from_.index('>')]
            else:
                from_name = None
                from_addr = from_

            if '<' in to and '>' in to:
                to_name = to[:to.index('<') - 1]
                to_addr = to[to.index('<') + 1:to.index('>')]
            else:
                to_name = None
                to_addr = from_

            logger.info('Message id %s, From %s (%s:%s), To %s (%s:%s), Subject %s',
                        message_id, from_, from_addr, from_name, to, to_addr, to_name, subject)

            email_map = {
                     'to': to,
                     'to_name': to_name, 'to_addr': to_addr,
                     'from': from_,
                     'from_name': from_name, 'from_addr': from_addr,
                     'subject': subject}

            if to_addr.startswith('open@'):
                self.open(email_map)
            elif to_addr.startswith('class-action@'):
                self.class_action(email_map)

            return



if __name__=='__main__':

    u = Users()
    u.add_subscription('a@gmail.com', 'nana')
    exit(0)
    ep = EmailParser()
    ep.parse('s3://ses-incoming-xwehyvyd/incoming-service/7dobnc6i91b7mmv91g7hj7tqmpbholdabokrn181')