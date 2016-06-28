import requests
import json

class BaseCmdbBackend(object):
    
    def __init__(self, url = 'http://127.0.0.1/'):
        self.url = url
   
    def get_serverinfo(self, query_list):
        path = 'cmdb/api/server_info'
        url = self.url + path
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(query_list), headers=headers)
        if r.status_code != 200:
            return []
        else:
            return r.json()
        