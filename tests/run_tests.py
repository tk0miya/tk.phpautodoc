#!/usr/bin/env python

import os
import re
import shutil
import unittest
from mock import Mock, patch
from functools import wraps
from tempfile import mkdtemp
from docutils.parsers.rst import Parser
from docutils.frontend import OptionParser
from docutils.utils import new_document
from sphinx.application import Sphinx
from sphinx.config import Config
import sphinxcontrib_phpautodoc as phpautodoc


class FakeSphinx(Sphinx):
    def __init__(self):
        self.config = Config(None, None, None, None)


def test_path_join(*args):
    return os.path.join(os.path.dirname(__file__), *args)


class TestPHPAutodoc(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.settings = OptionParser().get_default_values()
        self.settings.tab_width = 8
        self.settings.pep_references = False
        self.settings.rfc_references = False
        self.settings.env = Mock(srcdir=os.path.dirname(__file__),
                                 doctreedir=mkdtemp())

        self.app = FakeSphinx()
        phpautodoc.setup(self.app)

    def tearDown(self):
        shutil.rmtree(self.settings.env.doctreedir)

    @classmethod
    def add_testcase(cls, name):
        input_file_for = lambda filename: test_path_join('inputs', filename)
        expected_file_for = lambda filename: test_path_join('outputs', filename)

        @patch("sphinxcontrib_phpautodoc.ViewList")
        def test_runner(self, ViewList):
            doc = new_document('<test>', self.settings)
            src = open(input_file_for(name)).read()
            self.parser.parse(src, doc)

            results = "\n".join(args[0][0] for args in ViewList().append.call_args_list)
            expected = open(expected_file_for(name)).read()
            self.assertEqual(results, expected)

        funcname = "test_%s" % re.sub('[\.\-/]', '_', name, re.M)
        test_runner.__name__ = funcname
        setattr(cls, funcname, test_runner)


def add_testcase(arg, dirname, fnames):
    dirname = re.sub('.*?inputs/?', '', dirname)
    for filename in fnames:
        if filename[-4:] == ".rst":
            path = os.path.join(dirname, filename)
            TestPHPAutodoc.add_testcase(path)


# build up testcases
os.path.walk(test_path_join('inputs'), add_testcase, None)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPHPAutodoc)
    unittest.TextTestRunner(verbosity=2).run(suite)
