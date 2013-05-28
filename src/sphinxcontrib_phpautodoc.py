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

def comment2lines(node):
    for line in node.text.splitlines():
        if re.match('^\s*/?\*{1,2} ?', line):  # starts with '/**' or '/*' or '*' ?
            line = re.sub('\s*\*/.*$', '', line)  # remove '*/' of tail
            line = re.sub('^\s*/?\*{1,2} ?', '', line)  # remove '/**' or '/*' or '*' of top

            yield line


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


def is_same_mtime(path1, path2):
    try:
        mtime1 = os.stat(path1).st_mtime
        mtime2 = os.stat(path2).st_mtime

        return mtime1 == mtime2
    except:
        return False


def basename(path, ext=None):
    filename = os.path.basename(path)
    if ext:
        basename, _ext = os.path.splitext(filename)
        filename = "%s.%s" % (basename, ext)

    return filename


class AutodocCache(object):
    def parse_code(self, filename):
        import pickle
        from phply.phplex import lexer
        from phply.phpparse import parser

        basedir = self.state.document.settings.env.doctreedir
        cachename = os.path.join(basedir, basename(filename, 'parse'))
        if is_same_mtime(filename, cachename):
            tree = pickle.load(open(cachename, 'rb'))
        else:
            try:
                with codecs.open(filename, 'r', 'utf-8') as f:
                    tree = parser.parse(f.read(), lexer=lexer)

                with open(cachename, 'wb') as f:
                    pickle.dump(tree, f)
                mtime = os.stat(filename).st_mtime
                os.utime(cachename, (mtime, mtime))
            except:
                raise

        return tree


class PHPDocWriter(object):
    def add_line(self, line, indent_level=0):
        if line:
            indent = self.indent + u'   ' * indent_level
            self.result.append(indent + line, '<phpautodoc>')
        else:
            self.result.append('', '<phpautodoc>')

    def add_directive_header(self, directive, name, indent_level):
        domain = getattr(self, 'domain', 'php')
        self.add_line(u'.. %s:%s:: %s' % (domain, directive, name), indent_level)
        self.add_line('')

    def add_directive(self, directive, name, comment_node, indent_level=0):
        if not is_private_comment(comment_node):
            self.add_directive_header(directive, name, indent_level)

            if is_comment(comment_node):
                for line in comment2lines(comment_node):
                    self.add_line(line, indent_level + 1)
                self.add_line('')


class PHPAutodocDirective(Directive, AutodocCache, PHPDocWriter):
    has_content = False
    optional_arguments = 1

    def run(self):
        self.result = ViewList()
        self.indent = u''

        srcdir = self.state.document.settings.env.srcdir
        filename = os.path.join(srcdir, self.arguments[0])
        tree = self.parse_code(filename)
        self.traverse(tree)
        self.state.document.settings.env.note_dependency(filename)

        node = nodes.paragraph()
        node.document = self.state.document
        self.state.nested_parse(self.result, 0, node)

        return node.children

    def traverse(self, tree, indent=0):
        last_node = None
        for node in tree:
            if isinstance(node, ast.Function):
                self.add_directive('function', to_s(node), last_node, indent)
            elif isinstance(node, ast.Class):
                self.add_directive('class', node.name, last_node, indent)

                if not is_private_comment(last_node):
                    self.traverse(node.nodes, indent + 1)
            elif isinstance(node, ast.Method):
                self.add_directive('method', to_s(node), last_node, indent)
            elif isinstance(node, ast.ClassVariables):
                for variable in node.nodes:
                    self.add_directive('attr', variable.name, last_node, indent)

            last_node = node


def setup(app): 
    app.add_directive('phpautodoc', PHPAutodocDirective)
