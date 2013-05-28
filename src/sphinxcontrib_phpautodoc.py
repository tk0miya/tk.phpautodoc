# -*- coding: utf-8 -*-
"""
    sphinxcontrib_wikitable
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 by Takeshi KOMIYA
    :license: BSD, see LICENSE for details.
"""
import os
import re
import codecs
from phply import phpast as ast
from phply.phplex import lexer
from phply.phpparse import parser
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList


def is_comment(node):
    if isinstance(node, ast.Comment) and node.text[0:3] == '/**':
        return True
    else:
        return False


def is_private_comment(comment):
    if is_comment(comment):
        return re.search('@access\s+private', comment.text)
    else:
        return False


def to_s(node):
    if isinstance(node, ast.Constant):
        ret = node.name
    elif isinstance(node, ast.Array):
        elems = (to_s(n) for n in node.nodes)
        ret = "array(%s)" % ", ".join(elems)
    elif isinstance(node, ast.FormalParameter):
        ret = node.name
        if node.default:
            ret += ' = %s' % to_s(node.default)
    elif isinstance(node, (ast.Function, ast.Method)):
        if node.params is None:
            ret = node.name
        else:
            params = (to_s(p) for p in node.params)
            ret = "%s(%s)" % (node.name, ", ".join(params))
    else:
        ret = str(node)

    return ret


class PHPAutodocDirective(Directive):
    has_content = False
    optional_arguments = 1

    def run(self):
        self.result = ViewList()

        srcdir = self.state.document.settings.env.srcdir
        filename = os.path.join(srcdir, self.arguments[0])
        self.parse(filename)
        self.state.document.settings.env.note_dependency(filename)

        node = nodes.paragraph()
        node.document = self.state.document
        self.state.nested_parse(self.result, 0, node)

        return node.children

    def add_entry(self, directive, name, comment, indent):
        if not is_private_comment(comment):
            self.add_directive_header(directive, name, indent)
            self.add_comment(comment, indent)

    def add_line(self, line, level=0):
        indent = u'   ' * level
        self.result.append(indent + line, '<phpautodoc>')

    def add_directive_header(self, directive, name, indent):
        domain = getattr(self, 'domain', 'php')
        self.add_line(u'.. %s:%s:: %s' % (domain, directive, name), indent)
        self.add_line('')

    def add_comment(self, comment, indent):
        if not is_comment(comment):
            return

        for line in comment.text.splitlines():
            if re.match('^\s*/?\*+ ?', line):  # starts with '/*' or '*' ?
                line = re.sub('\s*\*/.*$', '', line)  # remove '*/' of tail
                line = re.sub('^\s*/?\*+ ?', '', line)  # remove '/*' or '*' of top

                if line:
                    self.add_line(line, indent + 1)
                else:
                    self.add_line('')

        self.add_line('')

    def parse(self, filename):
        try:
            with codecs.open(filename, 'r', 'utf-8') as f:
                tree = parser.parse(f.read(), lexer=lexer)

            self._parse(tree)
        except:
            raise

    def _parse(self, tree, indent=0):
        last_node = None
        for node in tree:
            if isinstance(node, ast.Function):
                self.add_entry('function', to_s(node), last_node, indent)
            elif isinstance(node, ast.Class):
                self.add_entry('class', node.name, last_node, indent)

                if not is_private_comment(last_node):
                    self._parse(node.nodes, indent + 1)
            elif isinstance(node, ast.Method):
                self.add_entry('method', to_s(node), last_node, indent)
            elif isinstance(node, ast.ClassVariables):
                for variable in node.nodes:
                    self.add_entry('attr', variable.name, last_node, indent)

            last_node = node


def setup(app): 
    app.add_directive('phpautodoc', PHPAutodocDirective)
