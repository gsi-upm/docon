from .models import TranslationRequest
from flask.ext.mongoengine.wtf import model_form

TRForm = model_form(TranslationRequest)
