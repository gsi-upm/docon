#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright 2014 J. Fernando Sánchez Rada - Grupo de Sistemas Inteligentes
#                                                       DIT, UPM
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import json
import sys
import os
import unicodecsv as csv
import codecs
import re
from datetime import datetime
from itertools import islice
from functools import partial

# import the logging library
import logging
# Get an instance of a logger
logging.basicConfig()
logger = logging.getLogger("docon")
logger.setLevel(logging.DEBUG)


def linesplit(value, separator=' '):
    return value.strip().split(separator)


def convert_date(value, informat="%d-%B-%Y", outformat="%Y-%m-%d-"):
    return datetime.strptime(value, informat).strftime(outformat)


def escapejs(val):
    try:
        return json.dumps(val)
    except Exception as ex:
        logger.error(ex)
        return "\"\""

def escapepy(val):
    return json.dumps(val, ensure_ascii=False)
    #return repr(val)[2:-1]


def get_client_ip(request):
    x_forwarded_for = request.headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.remote_addr
    return ip


def download_file(url):
    local_filename = os.path.join(settings.MEDIA_ROOT, url.split('/')[-1])
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:   # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename


def open_file(infile, informat='raw', encoding="utf-8", **kwargs):
    logger.debug('Opening file: {}'.format(infile))
    if isinstance(infile, basestring):
        if informat == "vnd.ms-excel" or informat == 'xls':
            import xlrd
            logger.debug('An office file!')
            f = xlrd.open_workbook(infile, on_demand=True)
        elif informat == "xml":
            logger.debug('An XML file!')
            f = etree.parse(infile)
        elif informat == "csv":
            logger.debug('Opening as csv')
            f = csv.reader(open(infile, 'r'),
                           encoding=encoding,
                           **kwargs)
        else:
            f = codecs.open(infile, 'r', encoding)
    else:
        if informat == "vnd.ms-excel" or informat == 'xls':
            import xlrd
            logger.debug('An office file!')
            f = xlrd.open_workbook(file_contents=infile.read(), on_demand=True)
        elif informat == "xml":
            logger.debug('An XML file!')
            f = etree.fromstring(infile)
        elif informat == "csv":
            logger.debug("CSV file")
            f = csv.reader(infile, encoding=encoding, **kwargs)
        else:
            f = codecs.iterdecode(iter(infile.readline, ""), encoding)
    return f


def get_template(template, infile):
    env = Environment(trim_blocks=True,
                      lstrip_blocks=True,
                      extensions=['jinja2.ext.do', ])
    env.globals['linesplit'] = linesplit
    env.globals['convert_date'] = convert_date
    env.globals['len'] = len
    env.globals['re'] = re
    env.globals['islice'] = islice
    env.filters['escapejs'] = escapejs
    env.filters['escapepy'] = escapepy
    env.globals['open_file'] = partial(open_file, infile)
    return env.from_string(template)

def translate_document(infile=None,
                       template=None,
                       template_data=None
                       ):
    if not template_data:
        template_data = {}
    logger.debug("PROCESSING!!")
    logger.debug("DATA!! %s" % template_data)

    template = get_template(template, infile)
    stream = template.stream(template_data)
    return stream


def get_client_ip(request):
    x_forwarded_for = request.headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.remote_addr
    return ip

def get_params(req, params):
    outdict = None
    if req.method == 'POST':
        outdict = req.form.copy()
    elif req.method == 'GET':
        outdict = req.args.copy()
    else:
        raise ValueError("Invalid data")
    outdict.update(req.files)
    wrongParams = {}
    for param, options in params.iteritems():
        for alias in options["aliases"]:
            if alias in outdict:
                outdict[param] = outdict[alias]
        if param not in outdict:
            if options.get("required", False):
                wrongParams[param] = params[param]
            else:
                if "default" in options:
                    outdict[param] = options["default"]
        else:
            if "options" in params[param] and \
                outdict[param] not in params[param]["options"] or \
                options.get("required", False) and not outdict[param]:
                wrongParams[param] = params[param]
    if wrongParams:
        message = {"status": "failed",
                   "message": "Missing or invalid parameters"}
        message["parameters"] = outdict
        message["errors"] = {param:error for param, error in wrongParams.iteritems()}
        raise ValueError(json.dumps(message, default=lambda x: []))
    return outdict


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        server = environ.get('HTTP_X_FORWARDED_SERVER', '')
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)
