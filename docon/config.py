CELERY_BROKER_URL = 'mongodb://localhost:27017/celery_broker'
CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/'
CELERY_MONGODB_BACKEND_SETTINGS = {
        'database': 'test_celery_backend',
        'taskmeta_collection': 'test_taskmeta_collection',
}
MONGODB_SETTINGS = {'DB': "test_db"}
SECRET_KEY = "KeepThisS3cr3t"
