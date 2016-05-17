#/usr/bin/env python
#!coding:utf-8
import os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from server import Server

if __name__ == '__main__':
    serv = Server()
    serv.start()
