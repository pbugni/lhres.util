pheme.util
==========

**Public Health EHR Message Engine (PHEME), utility library**

The ``pheme.util`` module provides a few executable utility programs
and several library methods used by other modules in the **pheme**
namespace.

Requirements
------------

`Python`_ 2.7.*

Install
-------

Use of a `virtualenv`_ is recommended.  After creating and activating
a virtual environment, clone and build the project in a directory of
choice::

    git clone https://github.com/pbugni/pheme.util.git
    cd pheme.util
    ./setup.py develop

Running
-------

The executable programs provided by ``pheme.util`` are listed under
[console_scripts] within the project's setup.py file.  All take the
standard help options [-h, --help].  Invoke with help for more
information::

    HL7_segment_parser --help

Testing
-------

From the root directory of ``pheme.util`` invoke the tests as follows::

    ./setup.py test

License
-------

BSD 3 clause license - See LICENSE.txt


.. _Python: http://www.python.org/download/releases/2.7/
.. _virtualenv: https://pypi.python.org/pypi/virtualenv