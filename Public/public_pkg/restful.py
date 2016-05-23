#!coding:utf-8
import requests
import json
import urlparse

CONTENT_TYPE = 'application/json'

def index(url, application, controller, params={}, content_type=None):
    if not content_type:
        content_type = CONTENT_TYPE
    req_url = urlparse.urljoin(urlparse.urljoin(url, application), controller)
    headers = {'content-type': content_type}
    print req_url
    return requests.get(req_url, params=params, headers=headers)
    
def show(url, application, controller, r_id, params={}, content_type=None):
    if not content_type:
        content_type = CONTENT_TYPE
    req_url = urlparse.urljoin(urlparse.urljoin(urlparse.urljoin(url, application), controller), r_id)
    headers = {'content-type': content_type}
    print req_url
    return requests.get(req_url, params=params, headers=headers)

def create(url, application, controller, data={}, content_type=None):
    if not content_type:
        content_type = CONTENT_TYPE
    req_url = urlparse.urljoin(urlparse.urljoin(url, application), controller)
    headers = {'content-type': content_type}
    print req_url
    return requests.get(req_url, data=json.dumps(data), headers=headers)

def update(url, application, controller, r_id, data={}, content_type=None):
    if not content_type:
        content_type = CONTENT_TYPE
    req_url = urlparse.urljoin(urlparse.urljoin(urlparse.urljoin(url, application), controller), r_id)
    headers = {'content-type': content_type}
    print req_url
    return requests.get(req_url, data=json.dumps(data), headers=headers)

def delete(url, application, controller, r_id, content_type=None):
    if not content_type:
        content_type = CONTENT_TYPE
    req_url = urlparse.urljoin(urlparse.urljoin(urlparse.urljoin(url, application), controller), r_id)
    headers = {'content-type': content_type}
    print req_url
    return requests.delete(req_url, headers=headers)



