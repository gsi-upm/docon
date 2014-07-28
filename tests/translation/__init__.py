import os
import time
import unittest
import tempfile
import StringIO
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
    with open(case + ".template", 'r') as f:
        template = f.read()
    stream = translate_document(case+".input", template)
    real_output = "".join(item for item in stream)
    print "Real: '{}'".format(real_output)
    with open(case+".output", 'r') as f:
        expected_output = f.read()
    print "Expected: '{}'".format(expected_output)
    assert real_output.strip() == expected_output.strip()

if __name__ == '__main__':
    unittest.main()
