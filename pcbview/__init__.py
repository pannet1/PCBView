"""pcbview — alias for openboardview_wasm (backwards compat)"""
from openboardview_wasm import *  # noqa: F401,F403
from openboardview_wasm._app import make_static_files_app  # noqa: F401
try:
    from openboardview_wasm import __version__  # noqa: F401
except: pass
