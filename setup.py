#!/usr/bin/env python

import os
from setuptools import setup

docs_require = ['Sphinx']
tests_require = ['nose', 'coverage']

try:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.txt')) as r:
        README = r.read()
except IOError:
    README = ''

setup(name='lhres.util',
      version='13.05',
      description="Utility functions for LHRES",
      long_description=README,
      license="BSD-3 Clause",
      namespace_packages=['lhres'],
      packages=['lhres.util', ],
      include_package_data=True,
      install_requires=['setuptools'],
      setup_requires=['nose'],
      tests_require=tests_require,
      test_suite="nose.collector",
      extras_require = {'test': tests_require,
                        'docs': docs_require,
                        },
      entry_points=("""
                    [console_scripts]
                    HL7_segment_parser=lhres.util.HL7_segment_parser:main
                    """),
)
