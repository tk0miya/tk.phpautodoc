# -*- coding: utf-8 -*-
"""
    sphinxcontrib_wikitable
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 by Takeshi KOMIYA
    :license: BSD, see LICENSE for details.
"""
import os
import re
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList


class PHPAutodocDirective(Directive):
    has_content = False
    optional_arguments = 1

    def run(self):
        self.indent = u''
        self.result = ViewList()

        srcdir = self.state.document.settings.env.srcdir
        filename = os.path.join(srcdir, self.arguments[0])
        self.parse(filename)

        node = nodes.paragraph()
        node.document = self.state.document
        self.state.nested_parse(self.result, 0, node)

        return node.children

    def add_line(self, line, *lineno):
        self.result.append(self.indent + line, '<phpautodoc>', *lineno)

    def add_directive_header(self, directive, name):
        domain = getattr(self, 'domain', 'php')
        self.add_line(u'.. %s:%s:: %s' % (domain, directive, name))
        self.add_line('')

    def add_comment(self, comment):
        text = comment.text
        text = re.sub('^//', '', text)
        text = re.sub('^/\*\s*', '', text)
        text = re.sub('\s*\*/$', '', text)

        r = re.compile('^\s*\*[ ]*', re.M)
        text = re.sub(r, '', text)

        for line in text.splitlines():
            self.add_line(u'   ' + line)

        self.add_line('')

    def parse(self, filename):
        from phply.phplex import lexer
        from phply.phpparse import parser

        try:
            with open(filename) as f:
                tree = parser.parse(f.read(), lexer=lexer)

            self._parse(tree)
        except:
            pass  # FIXME: ignore any errors

    def _parse(self, tree):
        from phply import phpast as ast

        last_node = None
        for node in tree:
            if isinstance(node, ast.Function):
                self.add_directive_header('function', node.name)

                if isinstance(last_node, ast.Comment):
                    self.add_comment(last_node)

            elif isinstance(node, ast.Class):
                self.add_directive_header('class', node.name)

                if isinstance(last_node, ast.Comment):
                    self.add_comment(last_node)

                self._parse(node.nodes)

            elif isinstance(node, ast.Method):
                self.add_directive_header('method', node.name)

                if isinstance(last_node, ast.Comment):
                    self.add_comment(last_node)

            last_node = node


def setup(app): 
    app.add_directive('phpautodoc', PHPAutodocDirective)
