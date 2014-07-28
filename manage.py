# Set the path
import os, sys
import logging
import logging.config

from flask.ext.script import Manager, Server
from translator.factory import create_app
from translator.models import User

if os.path.exists('logging.conf'):
    logging.config.fileConfig('logging.conf')
logging.getLogger("translator").addHandler(logging.NullHandler())
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

if __name__ == "__main__":
    manager.run()
