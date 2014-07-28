# -*- coding: utf-8 -*-
import time
from factory import create_celery_app
from .models import *
from .utils import translate_document
from datetime import timedelta, datetime
from StringIO import StringIO

celery = create_celery_app().celery

logger = celery.logger

@celery.task()
def process_request(tid):
    logger.warning("TR id: {}".format(tid))
    tr = TranslationRequest.objects.get(id=tid)
    tr.start()
    if tr.infile:
        infile = tr.infile
    else:
        infile = StringIO(tr.input)
    template = tr.template.text
    out = translate_document(infile=infile.get(),
                             template=template,
                             template_data=tr.to_mongo())
    tr.outfile.delete()
    tr.outfile.new_file(encoding="utf-8")
    for chunk in out:
        tr.outfile.write(chunk)
    tr.outfile.close()
    tr.save()
    tr.finish()
    logger.warning("Processed")
    return tr

@celery.task()
def clean_files():
    logger.warning("Cleaning files")
    olds = TranslationRequest.objects(infile__ne=None,
                                      finished__lte=(datetime.now()-timedelta(days=1)))
    logger.warning("Old files: {}".format(olds))
    for req in olds:
        req.clean_files()
    logger.warning("Cleaned")
