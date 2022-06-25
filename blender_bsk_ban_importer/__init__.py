__all__ = ("register", "unregister", "bl_info")


bl_info = {
    "name": "Silkroad BSK/BAN Importer",
    "author": "Iyad Ahmed (Twitter: @cgonfire)",
    "version": (0, 0, 1),
    "blender": (3, 1, 2),
    "location": "File > Import > Import BSK/BAN",
    "description": "",
    "category": "Import-Export",
}


import importlib
import sys
from traceback import print_exc
from typing import List


def module_register_factory(parent_module_name: str, module_names: List[str]):
    modules = [importlib.import_module(f"{parent_module_name}.{name}") for name in module_names]

    def register():
        for m in modules:
            try:
                m.register()
            except Exception:
                print_exc()

    def unregister():
        for m in reversed(modules):
            try:
                m.unregister()
            except Exception:
                print_exc()

    return register, unregister


module_names = ["operators", "panels"]
register_modules, unregister_modules = module_register_factory(__name__, module_names)


def register():
    register_modules()


def unregister():
    unregister_modules()
    for module_name in list(sys.modules.keys()):
        if module_name.startswith(__name__):
            del sys.modules[module_name]
