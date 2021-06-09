# -*- coding:utf-8 -*-

def get_class(modules_name):
    modules = __import__(modules_name, fromlist=True)
    if hasattr(modules, modules_name):
        return getattr(modules, modules_name)
    else:
        return None