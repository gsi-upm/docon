# -*- coding: utf-8 -*-
from flask import render_template, request, url_for, Blueprint, Response, jsonify
from utils import *
from .models import TranslationRequest, EuTemplate, EuFormat, OUTFORMATS
from celery.exceptions import TimeoutError
from bson.json_util import dumps
from languages import LANGUAGES
import logging
logger = logging.getLogger(__name__)

frontend = Blueprint('frontend', __name__, url_prefix='')
import tasks

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

@frontend.route('/upload')
def upload():
    return render_template('upload.html',
                           languages=LANGUAGES,
                           templates=EuTemplate.objects(),
                           informats=EuFormat.objects(),
                           outformats=OUTFORMATS)

@frontend.route('/formats')
def formats():
    return render_template('formats.html')

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
                            "options": ("json-ld"),
                            },
              "template": {"aliases": ("template", ),
                           "required": False
                            },
              "language": {"aliases": ("language", "l"),
                           "required": False,
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
    except ValueError as ex:
        return ex.message
    logger.info("Processing: {}".format(params))
    tr = TranslationRequest.from_params(params)
    tr.ip = get_client_ip(request)
    tr.save()
    trid = tr.id
    timeout = float(params["timeout"])
    if timeout >= 0:
        logger.info("Async")
        res = tasks.process_request.delay(trid)
        tr.task_id = res.task_id
        tr.save()
        try:
            res.get(timeout=timeout, propagate=False)
        except TimeoutError:
            pass
    else:
        tr = tasks.process_request(trid)
    return get_result(trid)

@frontend.route('/get/<translation_id>')
def get_result(translation_id):
    logger.info("Getting result for {}".format(translation_id))
    headers = {}
    try:
        tr = TranslationRequest.objects.get(id=translation_id)
        status = 202
        result = headers["Location"] = url_for("frontend.get_result",
                                    translation_id=translation_id)
        outfile = tr.outfile
        if outfile:
            status = 200
            result = outfile.get()
            logger.debug("Got response")
        else:
            logger.debug("Come back later")
    except Exception as ex:
        status = 404
        result = "Translation ID not found{}".format(ex)
    return Response(result, status=status, headers=headers)

@frontend.route('/my_requests')
def my_requests():
    ip = get_client_ip(request)
    reqs = TranslationRequest.objects(ip=ip)
    return jsonify(ip=ip, requests=list(req.as_dict() for req in reqs))
