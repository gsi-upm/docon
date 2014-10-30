import os
import time
import unittest
import tempfile
import StringIO
import difflib
import codecs
import json
from translator.utils import translate_document
from functools import partial
from os import listdir
from os.path import isfile, join, abspath, dirname
from fnmatch import fnmatch

TEST_PATH = dirname(abspath(__file__))

def test_generator():
    cases_dir = join(TEST_PATH, 'cases')
    for case in listdir(cases_dir):
        if fnmatch(case, "*.template"):
            yield check_case, case.rsplit(".", 1)[0]


def testOpen():
    infile = StringIO.StringIO("hello")
    template = "bye"
    outfile = StringIO.StringIO()
    stream = translate_document(infile, template)
    assert stream.next() == "bye"

def check_case(case):
    case = join(TEST_PATH, 'cases',  case)
    template_file = "{}.template".format(case)
    input_file = "{}.input".format(case)
    output_file = "{}.output".format(case)
    data_file = "{}.data".format(case)
    with codecs.open(template_file, 'r') as f:
        template = f.read()
    template_data = {}
    if isfile(data_file):
        with codecs.open(data_file, 'r') as f:
            template_data = json.load(f)
    stream = translate_document(input_file, template, template_data)
    real_output = u"".join(item for item in stream)
    print "Real: '{}'".format(real_output.encode("utf-8", errors="ignore"))
    with codecs.open(output_file, 'r', 'utf-8') as f:
        expected_output = f.read()
    print "Expected: '{}'".format(expected_output.encode("utf-8", errors="ignore"))

    diff = difflib.unified_diff(real_output, expected_output)
    thediff = "".join(line for line in diff)
    print("Difference:\n{}".format(thediff.encode("utf-8", errors="ignore")))
    assert real_output.strip() == expected_output.strip()

if __name__ == '__main__':
    unittest.main()
