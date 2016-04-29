#!coding:utf-8

import logging


class Console(object):
    
    def __init__(self):
        self.console = None
        self.db_backend = None
        self.format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
        self.datefmt = '%a, %d %b %Y %H:%M:%S'
        self.level = logging.DEBUG
        self.filename = None
        self.backend = [] # file, db
        self.filemode= None
        self.dbhost = None
        self.dbport = None
        self.dbname = None
        self.dbtable = None
    
    def create_backend_file(self, filename, filemode, level):
        self.filename = filename
        self.filemode = filemode
        if level == 'CRITICAL':
            self.level = logging.CRITICAL
        elif level == 'ERROR':
            self.level = logging.ERROR
        elif level == 'WARNING':
            self.level = logging.WARNING
        elif level == 'INFO':
            self.level = logging.INFO
        
        











     