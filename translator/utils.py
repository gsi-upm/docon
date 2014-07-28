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
import csv
import codecs
from datetime import datetime
from functools import partial

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('eurosentiment')


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


def open_file(infile, informat='csv', **kwargs):
    if isinstance(infile, basestring):
        if informat == "vnd.ms-excel" or informat == 'xls':
            import xlrd
            logger.debug('An office file!')
            f = xlrd.open_workbook(infile, on_demand=True)
        elif informat == "xml":
            logger.debug('An XML file!')
            f = etree.parse(infile)
        elif informat == "raw":
            f = open(infile, 'r')
        else:
            f = csv.reader(open(infile, 'r'), **kwargs)
    else:
        if informat == "xml":
            logger.debug('An XML file!')
            f = etree.fromstring(infile)
        else:
            f = infile
    return codecs.iterdecode(f, "utf-8")


def get_template(template, infile):
    env = Environment(trim_blocks=True,
                      lstrip_blocks=True,
                      extensions=['jinja2.ext.do', ])
    env.globals['linesplit'] = linesplit
    env.globals['convert_date'] = convert_date
    env.globals['len'] = len
    env.filters['escapejs'] = escapejs
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
    indict = None
    if req.method == 'POST':
        indict = req.form.copy()
    elif req.method == 'GET':
        indict = req.args.copy()
    else:
        raise ValueError("Invalid data")
    indict.update(req.files)
    outdict = {}
    wrongParams = {}
    for param, options in params.iteritems():
        for alias in options["aliases"]:
            if alias in indict:
                outdict[param] = indict[alias]
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
        raise ValueError(json.dumps(message))
    return outdict
