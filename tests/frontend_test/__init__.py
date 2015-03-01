import os
import time
import docon
import docon.factory
import unittest
import tempfile
import StringIO
from docon.utils import translate_document
from docon.factory import create_app
from mongoengine.connection import get_connection, disconnect


class FrontendTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app('config_test.py')
        self.app.debug = True
        self.client = self.app.test_client()

    def tearDown(self):
        connection = get_connection()
        connection.drop_database(self.app.config["MONGODB_SETTINGS"]["DB"])
        connection.drop_database(self.app.config["CELERY_BROKER_URL"].rsplit("/")[-1])
        connection.drop_database(self.app.config["CELERY_MONGODB_BACKEND_SETTINGS"]["database"])
        pass

    def testSimple(self):
        resp = self.client.get("/process?input=4&template=raw")
        print resp.data
        print resp.status_code
        assert 404 == resp.status_code

if __name__ == '__main__':
    unittest.main()
