from flask.ext.mongoengine import MongoEngine
from mongoengine.queryset import DoesNotExist
import datetime

from languages import LANGUAGES

db = MongoEngine()

OUTFORMATS = (
    ('json-ld', 'JSON-LD'),
    ('rdf', 'RDF+XML'),
    ('nt', 'N-Triples'),
    ('trix', 'TRIX'),
)

MIMES = {
    "json-ld": "application/json",
    "rdf": "application/rdf+xml",
    "default": "text/plain"
}

class EuFormat(db.Document):
    TXT = 'txt'
    CSV = 'csv'
    TSV = 'tsv'
    ODS = 'ods'
    XLS = 'xls'
    JSONLD = 'jsonld'
    XML = 'xml'
    fileformats = ((TXT, 'txt - Plain text'),
                   (CSV, 'csv - Comma Separated Values'),
                   (TSV, 'tsv - Tab Separated Values'),
                   (ODS, 'ods - Open Document Spreadsheet'),
                   (XLS, 'xls - Microsoft Excel Spreadsheet'),
                   (JSONLD, 'json-ld - JSON for Linked Data'),
                   (XML, 'XML - XML format'))

    name = db.StringField(verbose_name='Format name',
                          max_length=200,
                          unique=True)
    extension = db.StringField(verbose_name='File extension',
                               max_length=10,
                               choices=fileformats,
                               default=CSV)
    description = db.StringField(verbose_name='Description of the format',
                                 max_length=1500)
    example = db.FileField(verbose_name='Example of the format',
                           collection_name='example')

    def __unicode__(self):
        return self.name

    meta = {
        'allow_inheritance': True,
        'indexes': ['name'],
        'ordering': ['-name']
    }

class EuTemplate(db.Document):
    name = db.StringField(verbose_name='Template name',
                          max_length=200,
                          unique=True)
    text = db.StringField(verbose_name='Template')
    informat = db.ReferenceField(EuFormat,
                                 dbref=False,
                                 verbose_name='Input format')
    outformat = db.StringField(max_length=10, choices=OUTFORMATS,
                             verbose_name='Output format')
    usedTimes = db.IntField(verbose_name='Times it has been used',
                            default=0)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = "Conversion Template"


class TranslationRequest(db.Document):
    ERROR = "error"
    PENDING = "pending"
    SUCCESS = "success"
    INTYPES = (
        ('file', 'File'),
        ('url', 'Specify the file URL'),
        ('direct', 'Direct'),
    )

    template = db.ReferenceField(EuTemplate,
                                 verbose_name='Template used')
    input = db.StringField(verbose_name='Input')
    task_id = db.StringField(verbose_name='Task ID in Celery')
    intype = db.StringField(verbose_name='Input Type',
                            max_length=10,
                            choices=INTYPES, default='file')
    infile = db.FileField(verbose_name='Uploaded file for translation',
                          collection_name='uploads')
    outfile = db.FileField(verbose_name='Result of translation',
                           collection_name='results')
    informat = db.ReferenceField(EuFormat,
                                 verbose_name='Input format',
                                 required=False)
    outformat = db.StringField(max_length=10, choices=OUTFORMATS,
                               verbose_name='output format',
                               default='jsonld',
                               required=False)
    baseuri = db.StringField(verbose_name='Base URI',
                             max_length=200,
                             required=False)
    prefix = db.StringField(verbose_name='Prefix', max_length=20)
    language = db.StringField(verbose_name='Language of the corpus',
                              choices=LANGUAGES,
                              required=False)
    ip = db.StringField(verbose_name='Request IP')
    status = db.StringField(verbose_name='Status of the request')
    message = db.StringField(verbose_name='Return message')
    requested = db.DateTimeField(default=datetime.datetime.now)
    started = db.DateTimeField()
    finished = db.DateTimeField()


    def delete(self, *args, **kwargs):
        self.clean_files()
        super(TranslationRequest, self).delete(*args, **kwargs)

    def clean_files(self):
        self.infile.delete()
        self.outfile.delete()
        self.infile = self.outfile = None
        self.save()

    def delete(self, *args, **kwargs):
        self.clean_files()
        super(TranslationRequest, self).delete(*args, **kwargs)

    def start(self):
        self.started = datetime.datetime.now()
        self.status = self.PENDING
        self.save()

    def finish(self):
        self.finished = datetime.datetime.now()
        self.save()

    @staticmethod
    def from_params(params):
        fixed = params.copy()
        if "template" in fixed and not isinstance(fixed["template"],
                                                  db.ReferenceField):
            fixed["template"] = EuTemplate.objects.get(name=fixed["template"])
        if "informat" in fixed and not isinstance(fixed["informat"],
                                                   db.ReferenceField):
            fixed["informat"] = EuFormat.objects.get(name=fixed["informat"])
        if "input" in fixed and not isinstance(fixed["input"], basestring):
            fixed["infile"] = fixed["input"]
            del fixed["input"]
        return TranslationRequest(**fixed)

    def as_dict(self):
        return {"id": str(self.id),
                "started": self.started,
                "requested": self.requested,
                "finished": self.finished,
                "informat": self.informat.name,
                #"infile": self.infile,
                "outformat": self.outformat,
                "template": self.template.name,
                "status": self.status,
                "message": self.message}


class User(db.Document):
    login = db.StringField(unique=True)
    email = db.StringField()
    admin = db.BooleanField(default=False)
    password = db.StringField(min_length=3)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    # Required for administrative interface
    def __unicode__(self):
        return self.login
