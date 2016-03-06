import importlib
import inspect
import os

STATIC_FILES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
    'static'
)

from bottle import Bottle, static_file, redirect

from .mdl import mdl_to_dict

class Server:
    def __init__(self, mdl):
        self.bottle = Bottle()
        self._mdl = mdl_to_dict(mdl)

        self.bottle.route('/model', ['GET'], self.model)

        self.bottle.route('/<path:path>', ['GET'], self.static)
        self.bottle.route('/', ['GET'], lambda : redirect('/mdl_viewer.html'))

    def model(self):
        return self._mdl

    def static(self, path):
        return static_file(path, root=STATIC_FILES_PATH)

    def run(self, *args, **kwargs):
        return self.bottle.run(*args, **kwargs)
