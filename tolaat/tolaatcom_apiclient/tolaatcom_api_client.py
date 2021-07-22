import requests

import logging

class TolaatComApiClient:

    def __init__(self):
        self.root = 'http://127.0.0.1:5000'
        self.headers = {'Content-Type': 'application/json'}

        self.logger = logging.getLogger('tolaatcom.api.client')


    def _post(self, sector, command, j):
        self.path = f'{self.root}/api/1.0/{sector}/{command}'
        self.logger.info('Sending to %s/%s: %s', sector, command, j)
        r = requests.post(self.path, headers=self.headers, json=j)
        r.raise_for_status()
        self.logger.info('OK')
        return r.json()

    def get_view(self, view):
        r = self._post('db', 'get-view', view)
        return r


    def search_views(self, type, search_string, page, page_size):
        r = self._post('search', 'search-views', {'type': type, 'search_string': search_string,
                                                  'page': page, 'page_size': page_size})

        return r

if __name__=='__main__':

    client = TolaatComApiClient()
    client.get_view(1,2)
