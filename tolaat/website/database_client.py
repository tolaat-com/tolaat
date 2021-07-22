
from flask import current_app, g, abort
import boto3
import zlib
import json
import base64

from tolaatcom_nhc import dynamo_help

from tolaatcom_apiclient import tolaatcom_api_client
from website import database_common


class DynamoDatabase:

    def __init__(self):
        self.apiclient = tolaatcom_api_client.TolaatComApiClient()


    def get_view(self, view_id):
        return self.apiclient.get_view(view_id)

    def get_entity(self, type, name, page=0):
        return self.apiclient.get_entity(type, name, page)

    def close(self):
        pass



class SelectSearchEngine:

    def __init__(self):
        self.apiclient = tolaatcom_api_client.TolaatComApiClient()

    def search_views(self, type, search_string, page, page_size):
        return self.apiclient.search_views(type, search_string, page, page_size)

