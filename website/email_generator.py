import boto3
import json
from jinja2 import Environment, PackageLoader, select_autoescape

class EmailGenerator:

    def __init__(self, date):
        self.session = boto3.Session()
        self.dynamodb = self.session.client('dynamodb')
        self.tablename = 'changes'
        self.date = date

    def load(self):
        today = self.date.strftime('%Y%m%d')
        key = {'u': {'S': f'itz:{today}'}}
        r = self.dynamodb.get_item(TableName=self.tablename, Key=key)
        if 'Item' not in r:
            return

        cases = []
        for k, v in r['Item'].items():
            if k == 'u':
                continue
            d = json.loads(v['S'])
            d['caseid'] = k
            cases.append(d)

        return cases

    def generate_emails(self):
        cases = self.load()
        env = Environment(
            loader=PackageLoader('changes', 'email-templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

        subject_template = env.get_template('class-action.subject')
        subject = subject_template.render(cases=cases)
        html_template = env.get_template('class-action.html')
        html = html_template.render(cases=cases)
        txt_template = env.get_template('class-action.txt')
        txt = txt_template.render(cases=cases)

        s1 = boto3.Session(region_name='us-east-1')
        ses = s1.client('ses')

        ses.send_email(
                Source='x@tl8.me',
                Destination={'ToAddresses': ['andyworms@gmail.com']},
                Message={
                'Subject': { 'Data': subject,'Charset': 'utf-8'},
                'Body': { 'Text': {  'Data': txt, 'Charset': 'utf-8' },
                'Html': { 'Data': html, 'Charset': 'utf-8' }}})

        return subject, html, txt


if __name__=='__main__':
    import datetime
    d = datetime.date(2021, 1, 30)

    eg = EmailGenerator(d)
    eg.generate_emails()
    #eg.load()
