# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~

    A simple WSGI module
"""

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from translator import factory
import os.path
import logging.config

if os.path.exists('logging.conf'):
    logging.config.fileConfig('logging.conf')
logging.getLogger("translator").addHandler(logging.NullHandler())

application = factory.create_app()

if __name__ == "__main__":
    run_simple('0.0.0.0', 5000, application, use_reloader=True, use_debugger=True)

