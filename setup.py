# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys
import pkg_resources


setup(
     name='tk.phpautodoc',
     version='0.0.4',
     description='sample implementation of phpdocumentor using sphinx',
     author='Takeshi Komiya',
     author_email='i.tkomiya at gmail.com',
     url='https://bitbucket.org/tk0miya/tk0.phpdoc',
     license='Apache License 2.0',
     py_modules=['sphinxcontrib_phpautodoc'],
     packages=find_packages('src'),
     package_dir={'': 'src'},
     include_package_data=True,
     install_requires=(
         'ply',
     ),
)
