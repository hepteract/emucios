#!/usr/bin/env python2

import requests

class Response(object):
    def __init__(self, response):
        self.__response = response

    def __repr__(self):
        return self.__response.text

    def __getattr__(self, name):
        return getattr(self.__response, name)

    def __getitem__(self, name):
        return self.__response[name]

class CurlInterface(object):
    def __init__(self):
        self.ret = None
    def __getitem__(self, name):
        try:
            return Response(requests.get(\
                "http://" + name.replace(";", "/").replace("\;", ";")))
        except:
            return -1

    def __setitem__(self, name, value):
        try:
            self.ret = requests.post(\
            "http://" + name.replace(";", "/").replace("\;", ";"), data = value)
        except:
            self.ret = -1

    def keys(self):
        return ()

class NetworkInterface(object):
    def __getitem__(self, name):
        if name == "http":
            return CurlInterface()
        else:
            pass

    def keys(self):
        return ("http",)

def read():
    return NetworkInterface()

def write(content):
    pass
