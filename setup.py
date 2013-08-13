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

setup(name='pheme.util',
      version='13.05',
      description="Utility functions for PHEME",
      long_description=README,
      license="BSD-3 Clause",
      namespace_packages=['pheme'],
      packages=['pheme.util', ],
      include_package_data=True,
      install_requires=['setuptools', 'lockfile'],
      setup_requires=['nose'],
      tests_require=tests_require,
      test_suite="nose.collector",
      extras_require = {'test': tests_require,
                        'docs': docs_require,
                        },
      entry_points=("""
                    [console_scripts]
                    HL7_segment_parser=pheme.util.HL7_segment_parser:main
                    configvar=pheme.util.config:configvar
                    """),
)
