import mod

def get_class(module_name, class_name):
    if hasattr(module_name, class_name):
        return getattr(module_name, class_name)
    else:
        return None

def get_

cls = get_class(mod, 'Mod')
mod = cls()
mod.log()