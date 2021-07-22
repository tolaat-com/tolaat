import boto3
import json
import pickle

class Unlock:

    def __init__(self):
        self.session = boto3.Session()
        self.dynamodb = self.session.client('dynamodb')

    def unlock(self):
        key = {'case_id': {'n': '67104-01-20'}}
        r = self.dynamodb.get_item(TableName='ugc', Key={'u': {'S': json.dumps(key)}})
        item = r['Item']
        for k, v in item['contributions']['M'].items():
            if 'uploaded' in v['M'] and v['M']['uploaded']['S'] == '23/05/2021':
                if 'censored' in v['M']:
                    value = v['M']['censored']['BOOL']
                    print(f'{value} {type(value)}')
                    del v['M']['censored']

        print(pickle.dumps(item))
        self.dynamodb.put_item(TableName='ugc', Item=item)

if __name__=='__main__':
    u = Unlock()
    u.unlock()