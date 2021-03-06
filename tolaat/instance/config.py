import os

from dotenv import load_dotenv

load_dotenv()

MAJOR = '20210715_150022'
MINOR = '0'

SERVER = os.environ.get('SERVER', '1')
if SERVER == '1':
    print ('Running as server')
else:
    print('Running as client')

DEFAULT_REGION = 'eu-central-1'
DEFAULT_BUCKET = 'cloud-eu-central-1-q97dt1m5d4rndek'

VIEWS_TABLE = f'full_views_v{MAJOR}.{MINOR}'
DOCUMENTS_BUCKET = 'cloud-eu-central-1-q97dt1m5d4rndek'
DOCUMENTS_PREFIX = 'documents/destination_v2'
MASTER_TABLE = f'master_table'
SEARCH_PATH = f'documents/search_{MAJOR}.{MINOR}''/searchable/{type}_gzip/{type}_gzip.gz'

UGC_TABLE='ugc'
UGC_BUCKET = 'eu-central-1-ugc'
UGC_PREFIX='ugc'

RECAPTCHA_PUBLIC_KEY='6LeMmrAZAAAAAHzEIJ9qUNplIIx713dryPXqMgil'
RECAPTCHA_PRIVATE_KEY = os.environ['RECAPTCHA_PRIVATE_KEY']
RECAPTCHA_PARAMETERS = {'hl': 'iw', 'render': 'onload'}
RECAPTCHA_DATA_ATTRS = {'theme': 'light'}
