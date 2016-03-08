import importlib
import inspect
import os

STATIC_FILES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
    'static'
)

from bottle import Bottle, static_file, redirect, response

from .mdl import mdl_to_dict
from .mtrl import mtrl_to_dict
from .tex import tex_to_dict

class Server:
    def __init__(self, rsc_manager):
        self.bottle = Bottle()
        self.rsc_manager = rsc_manager

        self.bottle.route('/model/<path:path>', ['GET'], self.model)
        self.bottle.route('/mtrl/<path:path>', ['GET'], self.mtrl)
        self.bottle.route('/tex/<path:path>', ['GET'], self.tex)
        self.bottle.route('/tex_data/<path:path>', ['GET'], self.tex_data)

        self.bottle.route('/<path:path>', ['GET'], self.static)
        self.bottle.route('/', ['GET'], lambda : redirect('/mdl_viewer.html'))

    def model(self, path):
        return mdl_to_dict(self.rsc_manager.get_model(path))

    def mtrl(self, path):
        return mtrl_to_dict(self.rsc_manager.get_material(path))

    def tex(self, path):
        return tex_to_dict(self.rsc_manager.get_texture(path))

    def tex_data(self, path):
        response.content_type = 'application/octet-stream'
        return bytes(self.rsc_manager.get_texture(path).mipmap(0))

    def static(self, path):
        return static_file(path, root=STATIC_FILES_PATH)

    def run(self, *args, **kwargs):
        return self.bottle.run(*args, **kwargs)
