# Set the path
import os, sys
import logging
import logging.config

from flask.ext.script import Manager, Server
from docon.factory import create_app
from docon.models import User, TranslationRequest

if os.path.exists('logging.conf'):
    logging.config.fileConfig('logging.conf')
logging.getLogger("docon").addHandler(logging.NullHandler())
app = create_app()
manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = '0.0.0.0')
)

@manager.option('-a', '--admin', help='Admin username')
@manager.option('-p', '--password', help='Admin password')
@manager.option('-e', '--email', help='Admin email')
def init_users(admin,  email, password):
    admin = User(admin, email, True, password)
    admin.save()

@manager.command
def clean_files():
    for tr in TranslationRequest.objects:
        tr.clean_files()

@manager.command
def clean_requests():
    for tr in TranslationRequest.objects:
        tr.delete()

if __name__ == "__main__":
    manager.run()
