import os
import time
import translator
import translator.factory
from translator.utils import translate_document
import unittest
import tempfile
import StringIO
from mongoengine.connection import get_connection, disconnect


class TranslatorTest(unittest.TestCase):

    def setUp(self):
        self.app = translator.factory.create_app('config_test.py')
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
