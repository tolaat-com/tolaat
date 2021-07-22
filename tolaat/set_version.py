from os.path import join, dirname, abspath
import boto3

dynamodb = boto3.client('dynamodb')

def get_latest_table():
    paginator = dynamodb.get_paginator('list_tables')
    tables = []
    for r in paginator.paginate():
        for table in r['TableNames']:
            if table.startswith('full_views_'):
                desc = dynamodb.describe_table(TableName=table)
                dt = desc['Table']['CreationDateTime']
                tables.append((table, dt))

    tables.sort(key=lambda x:x[1], reverse=True)
    latest = tables[0][0]
    latest = latest.replace('full_views_v', '')
    latest = latest.split('.')[0]
    return latest


def replace():
    latest = get_latest_table()
    d = dirname(__file__)
    template_file = join(d, 'instance', 'config.py_template')
    template = open(template_file, 'r').read()

    config = template.replace('RUNVERSION', latest)
    output_file = template_file.replace('_template', '')
    open(output_file, 'w').write(config)
    print(f'Configured version {latest} to file {abspath(output_file)}')



if __name__=='__main__':
    replace()
