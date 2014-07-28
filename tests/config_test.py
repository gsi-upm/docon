CELERY_BROKER_URL = ''
CELERY_RESULT_BACKEND = ''
CELERY_ALWAYS_EAGER = True
CELERY_MONGODB_BACKEND_SETTINGS = {
        'database': 'test_celery_backend',
        'taskmeta_collection': 'test_taskmeta_collection',
}
MONGODB_SETTINGS = {'DB': "test_db"}
SECRET_KEY = "KeepThisS3cr3t"
