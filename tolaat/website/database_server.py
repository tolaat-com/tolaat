
from flask import current_app, g, abort
import boto3
import zlib
import json
import base64

from tolaatcom_nhc import dynamo_help



class DynamoDatabase:

    def __init__(self):
        self.views_table = current_app.config['VIEWS_TABLE']
        self.master_table = current_app.config['MASTER_TABLE']

        self.region = current_app.config['DEFAULT_REGION']
        self.dynamo = boto3.client('dynamodb', region_name=self.region)


    def assert_not_deleted(self, d):
        if 'data' in d and 'deleted' in d['data']:
            abort(404)

    def get_view(self, view_id):
        key = json.dumps(view_id)
        g.key = base64.b64encode(key.encode('utf-8')).decode('utf-8')
        request_items = {self.views_table: {'Keys': [{'view_id': {'S': key}}]}}

        if True and 'case_id' in view_id:
            case_id = view_id['case_id']
            if 'n' in case_id:
                master_view = f'n:{case_id["n"]}'
            elif 't' in case_id:
                master_view = f't:{case_id["t"]}'
            else:
                master_view = None

            if master_view is not None:
                fields = 'api', 'by_date', 'data', 'permissions'
                request_items[self.master_table] = {'Keys': [{'case_id': {'S': master_view}}],
                                                'ProjectionExpression': ', '.join([f'#{f}' for f in fields]),
                                                'ExpressionAttributeNames': {f'#{f}': f for f in fields}}


        resp = self.dynamo.batch_get_item(RequestItems=request_items)
        responses = resp['Responses']
        if responses[self.views_table] or responses.get(self.master_table):
            result = {}
            if responses.get(self.views_table):
                record = responses[self.views_table][0]

                result = dynamo_help.DynamoHelp.item_to_obj(record)
                if type(result.get('data')) == bytes:
                    result['data'] = json.loads(zlib.decompress(result['data']).decode('utf-8'))

            if responses.get(self.master_table):
                master = responses[self.master_table][0]
                result['from_master'] = dynamo_help.DynamoHelp.item_to_obj(master)
                if 'data' in result['from_master']:
                    d = result['from_master']['data']
                    d = zlib.decompress(d)
                    d = d.decode('utf-8')
                    result['from_master']['data'] = json.loads(d)

            if result.get('from_master', {}).get('permissions', {}).get('deleted'):
                abort(404)

            return result
        else:
            abort(404)

    def get_entity(self, type, name, page=0):
        k = {'t': type, 'n': name, 'p': page}
        return self.get_from_obj(k)

    def get_from_obj(self, k):
        if 'p' not in k:
            k['p'] = 0
        k = json.dumps(k)
        r2 = self.dynamo.batch_get_item(
            RequestItems={
                self.views_table: {'Keys': [{'view_id': {'S': k}}]},
            })

        responses = r2['Responses']
        item = responses[self.views_table][0]
        return item


    def close(self):
        del self.dynamo

class SelectSearchEngine:

    def __init__(self):
        self.search_bucket = current_app.config['DEFAULT_BUCKET']
        self.search_path = current_app.config['SEARCH_PATH']
        self.region = current_app.config['DEFAULT_REGION']
        self.s3 = boto3.Session(region_name=self.region).client('s3')

    def search_string_to_condition(self, search_string):
        search_string = search_string.replace("'", "_")
        search_strings = search_string.split(' וגם ')
        parts = [f"s.name like '%{s}%'" for s in search_strings]
        condition = " and ".join(parts)
        return condition


    def search_views(self, type, search_string, page, page_size):
        condition = self.search_string_to_condition(search_string)
        expression = f'select s.* from S3Object s where {condition}'
        key = self.search_path.format(type=type)
        return self.s3_select(key, expression, page, page_size)

    def s3_select(self, key, expression, page, page_size):
        limit = page * page_size + 1
        response = self.s3.select_object_content(
            Bucket=self.search_bucket,
            Key=key,
            InputSerialization={'JSON': {'Type': 'Lines'}, 'CompressionType': 'GZIP'},
            OutputSerialization={'JSON': {'RecordDelimiter': '\n'}},
            Expression=f'{expression} LIMIT {limit}',
            ExpressionType='SQL'
        )
        found = 0
        records_to_skip = (page - 1) * page_size
        skipped = 0
        pending = ''
        for event in response['Payload']:
            if 'Records' in event:
                records = event['Records']['Payload'].decode('utf-8')
                for j in records.split('\n'):
                    if not j:
                        continue
                    if skipped < records_to_skip:
                        skipped += 1
                        continue
                    try:
                        j = json.loads(f'{pending}{j}')
                        pending = ''
                    except json.decoder.JSONDecodeError as e:
                        pending = j
                        continue
                    yield j
                    found += 1
                    if found > page_size:
                        break




