# -*- coding:utf-8 -*-

def get_class(module_name, class_name):
    if hasattr(module_name, class_name):
        return getattr(module_name, class_name)
    else:
        return None