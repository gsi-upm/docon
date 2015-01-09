# -*- coding: utf-8 -*-
from flask import (abort, Blueprint, Flask, jsonify,
                   make_response, redirect, render_template,
                   request, Response, url_for)
from utils import *
from .models import TranslationRequest, EuTemplate, EuFormat, OUTFORMATS, db
from celery.exceptions import TimeoutError
from bson.json_util import dumps
from languages import LANGUAGES
from bson import json_util
from bson import ObjectId
from gridfs import GridFS
from gridfs.errors import NoFile

import logging
logger = logging.getLogger(__name__)

frontend = Blueprint('frontend', __name__, url_prefix='')
import tasks
import models

@frontend.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # login and validate the user...
        login_user(user)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("frontend.index"))
    return render_template("login.html", form=form)

@frontend.route('/')
def home():
    return render_template('home.html')

@frontend.route('/examples/<fmt>')
def serve_example(fmt):
    try:
        example = EuFormat.objects.get(name=fmt).example.get()
        response = make_response(example.read())
        response.mimetype = example.content_type
        return response
    except (EuFormat.DoesNotExist, NoFile):
        return "No file for {}".format(fmt)
        #abort(404)

@frontend.route('/upload')
def upload():
    return render_template('upload.html',
                           languages=LANGUAGES,
                           templates=EuTemplate.objects(),
                           informats=EuFormat.objects(),
                           outformats=OUTFORMATS)

@frontend.route('/formats')
def formats():
    formats = EuFormat.objects.all()
    return render_template('formats.html', formats=formats)

@frontend.route('/api')
def api():
    return render_template('api.html')

@frontend.route('/process', methods=['POST', 'GET'])
def process():
    PARAMS = {"input": {"aliases": ("i", "input"),
                        "required": True,
                        "help": "Input text"
                        },
              "informat": {"aliases": ("f", "informat"),
                           "required": False, },
              "intype": {"aliases": ("intype", "t"),
                         "required": False,
                         "default": "direct",
                         "options": ("direct", "url", "file"),
                         },
              "outformat": {"aliases": ("outformat", "o"),
                            "default": "json-ld",
                            "required": False,
                            },
              "template": {"aliases": ("template", ),
                           "required": False
                            },
              "language": {"aliases": ("language", "l"),
                           "required": False,
                           },
              "baseuri": {"aliases": ("base", "b", "baseuri"),
                           "required": False,
                           "default": "http://demos.gsi.dit.upm.es/eurosentiment/generator/process/default#",
                            },
              "urischeme": {"aliases": ("urischeme", "u"),
                            "required": False,
                            "default": "RFC5147String",
                            "options": ("RFC5147String",)
                            },
              "timeout": {"aliases": ("timeout", ),
                          "required": False,
                          "default": "0"
                          },
              }
    try:
        params = get_params(request, PARAMS)
        if "language" in params and params["language"] == "":
            del params["language"]
        if "template" not in params:
            informat = EuFormat.objects.get(name=params["informat"])
            params["template"] = EuTemplate.objects.get(informat=informat,
                                                        outformat=params["outformat"]).name
    except ValueError as ex:
        return ex.message
    logger.info("Processing: {}".format(params))
    try:
        tr = TranslationRequest.from_params(params)
    except EuTemplate.DoesNotExist as ex:
        return ex.message, 404
    tr.ip = get_client_ip(request)
    tr.save()
    trid = tr.id
    try:
        timeout = float(params["timeout"])
        logger.info("Async")
        res = tasks.process_request.delay(trid)
        tr.task_id = res.task_id
        tr.save()
        try:
            res.get(timeout=timeout, propagate=False)
        except TimeoutError:
            pass
    except ValueError:
        tr = tasks.process_request(trid)
    return get_result(trid)

@frontend.route('/get/<translation_id>')
def get_result(translation_id):
    logger.info("Getting result for {}".format(translation_id))
    headers = {}
    mimetype = "text/html"
    try:
        tr = TranslationRequest.objects.get(id=translation_id)
        headers["Location"] = url_for("frontend.get_result",
                                    translation_id=translation_id)
        result = json.dumps(tr.as_dict(), default=json_util.default)
        status = tr.status
        if status == tr.SUCCESS:
            outfile = tr.outfile
            mimetype = models.MIMES.get(tr.outformat, models.MIMES["default"])
            status = 200
            result = outfile.get()
            logger.debug("Got response")
        elif status == tr.PENDING:
            status = 202
            logger.debug("Come back later")
        else:
            status = 500
            logger.debug("There was an error processing the request.")

    except Exception as ex:
        status = 404
        result = "Translation ID not found: {}".format(ex)
    return Response(result, status=status, headers=headers, mimetype=mimetype)

@frontend.route('/my_requests')
def my_requests():
    ip = get_client_ip(request)
    reqs = TranslationRequest.objects(ip=ip).order_by("-started")
    return jsonify(ip=ip, requests=list(req.as_dict() for req in reqs))
