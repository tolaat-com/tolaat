from os import environ
from website import create_app


port = environ.get('PORT', 5000)
host = environ.get('HOST', '127.0.0.1')

client = environ.get('SERVER', '1') != '1'

if client:
    environ['SERVER'] = '0'
    environ['AWS_SHARED_CREDENTIALS_FILE'] = 'no_aws_credentials.txt'
    environ['AWS_PROFILE'] = 'no'


app = create_app()
app.run(port=port, host=host)