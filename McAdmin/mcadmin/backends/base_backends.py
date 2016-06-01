import requests
import json

class BaseCmdbBackend(object):
    
    url = 'http://127.0.0.1/'
    
    def __init__(self):
        pass
    
    def get_serverinfo(self, request_body):
        path = 'cmdb/api/server_info'
        url = self.url + path
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(request_body), headers=headers)
        if r.headers['status'] != 200:
            return []
        else:
            return r.json()
        