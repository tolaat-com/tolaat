import logging
import sys
logging.basicConfig(level=logging.DEBUG,
                    format='X %(asctime)s: %(levelname)s %(process)d:%(threadName)s [%(name)s] - %(message)s',
                    stream=sys.stdout)
logging.info('Started logging system')

logging.getLogger('botocore').setLevel(logging.WARN)
logging.getLogger('werkzeug').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.WARN)
logging.getLogger('s3transfer').setLevel(logging.WARN)

