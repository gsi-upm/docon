from flask import Flask, current_app, has_app_context
from celery import Celery
from celery.utils.log import get_task_logger
from .utils import ReverseProxied
import logging
import os
logger = logging.getLogger(__name__)

def create_app(config_filename='config.py', settings_override=None):
    logger.info("Creating app")
    app = Flask(__name__)
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    config_path = os.path.abspath(config_filename)
    if not os.path.isfile(config_path):
        config_path = config_filename
    logger.debug("Using config: {}".format(config_path))
    app.config.from_pyfile(config_path)
    app.config.from_object(settings_override)
    with app.app_context():
        import views
        import admin
        from .models import db
        from .auth import init_login
    app.register_blueprint(views.frontend)
    db.init_app(app)
    init_login(app)
    admin.make_admin(app)
    return app


def create_celery_app(flask_app=None):
    logger.debug("Creating celery app")
    if not flask_app:
        if has_app_context():
            logger.debug("Using current flask app")
            app = current_app
        else:
            logger.debug("No current flask app")
            app = create_app()
    else:
        app = flask_app
    celery = Celery(app.import_name,
                    broker=app.config['CELERY_BROKER_URL'],
                    backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    celery.logger = get_task_logger(__name__)
    app.celery = celery
    return app
