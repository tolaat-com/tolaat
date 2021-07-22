from os import environ
from website import create_app

environ['SERVER'] = '0'

# so at least we can initialize
# aws sessions (even if never
# used)
environ['AWS_SHARED_CREDENTIALS_FILE'] ='no_aws_credentials.txt'
environ['AWS_PROFILE'] ='no'

app = create_app()
app.run(port=environ.get('PORT', 5005))