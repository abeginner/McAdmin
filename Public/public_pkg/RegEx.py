#-*-coding:utf-8-*-
import re

__all__ = ['RegInterIpA', 'RegInterIpC', 'RegIp']

def __init__():
    pass

#Regular Expressions of Class A private address
def RegInterIpA(ip):
    reip = re.compile(r"^10\.((([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))\.){2}(([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))$")
    return re.match(reip, ip)

#Regular Expressions of Class C private address
def RegInterIpC(ip):
    reip = re.compile(r"^192\.168\.((([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))\.)(([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))$")
    return re.match(reip, ip)

#Regular Expressions of IP address
def RegIp(ip):
    reip = re.compile(r"((([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))\.){3}(([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))$")
    return re.match(reip, ip)

#Regular Expressions of url
