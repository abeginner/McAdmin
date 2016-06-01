from base_backends import BaseCmdbBackend

class CmdbBackend(BaseCmdbBackend):
    pass

    """
    if you not use the default cmdb, you must rewrite the methods as blow:
    
    def get_serverinfo(self, request_body):
    it accept the request_body parameter as this format:
    {'ips':[], 'bussiness':[], 'server_code':int, 'idc':str, 'status':str, 'tech_admin':str, 'sysop_admin:':str}
    and return a list as this format:
    
    
    """