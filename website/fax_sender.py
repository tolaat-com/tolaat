import requests
import re
import logging

logger = logging.getLogger('fax_sender')

class FaxSender:

    def __init__(self):
        self.email='andy.worms@gmail.com'
        self.password='myfaxman'

        self.base_url = 'https://www.myfax.co.il/action'
        self.send_url = f'{self.base_url}/faxUpload.do'
        self.status_url = f'{self.base_url}/faxStatus.do?v=1'

    def get_status(self, faxcode):
        body = {'email': f'{self.email}', 'password': f'{self.password}', 'faxCode': f'{faxcode}'}


        statuses = {
            '0' : 'INIT',
            '1' : 'CONFIRM',
            '2' : 'NO_ANSWER',
            '3' : 'BUSY',
            '4' : 'CONNECT',
            '6' : 'WRONG_NUMBER',
            '7' : 'FAIL',
            '9' : 'SENT',
            '10': 'DELETE'
        }

        statuses_h = {
            '0': 'איתחול',
            '1': 'התחברות',
            '2': 'אין מענה',
            '3': 'קו תפוס',
            '4': 'מתחבר',
            '6': 'מספר שגוי',
            '7': 'נכשל',
            '9': 'נשלח בהצלחה',
            '10': 'נמחק'
        }

        r = requests.post(self.status_url, data=body)

        text = r.text
        m = self.parse(text)
        status = m['FAX_STATUS']
        status_name = statuses.get(status, '')
        status_name_h = statuses_h.get(status, '')

        m['FAX_STATUS_NAME'] = status_name
        m['FAX_STATUS_NAME_H'] = status_name_h

        return m

    def parse(self, xml):
        r = re.findall('[<]([_A-Z]+)[>]([^<]+)[<][/]', xml, re.MULTILINE)
        m = {}
        for k, v in r:
            m[k] = v

        return m

    def send_fax(self, faxNumber, url):

        if False:
            last_char = faxNumber[-1]
            if last_char == '0':
                last_char = '1'
            else:
                last_char = '0'
            faxNumber = f'{faxNumber[:-1]}{last_char}'

        body = {'email': self.email, 'password': self.password,
                'faxNumber': faxNumber, 'fileURL': url}

        logger.info('Sending ')
        r = requests.post(self.send_url, data=body)
        logger.info(r.status_code)
        logger.info(dict(r.headers))
        text = r.text
        return self.parse(text)


if __name__=='__main__':
    f = FaxSender()

    #f.parse(e)
    #m = f.send_fax()
    #print(m)
    m = f.get_status('3cf6c2ae-f5f5-4eda-8bb7-1df31c830e79')
    print(m)
    print(m['FAX_STATUS_NAME'])