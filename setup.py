#### virtualenv-commands
#### Setup Script

### Copyright (c) 2009, Coptix, Inc.  All rights reserved.
### See the LICENSE file for license terms and warranty disclaimer.

from __future__ import absolute_import
from setuptools import setup, find_packages

setup(
    name = 'virtualenv-commands',
    version = '0.2.3',
    description = 'Additional commands for virtualenv.',
    author = 'Medium',
    author_email = 'labs@thisismedium.com',
    url = 'http://thisismedium.com/labs/virtualenv-commands/',
    license = 'BSD',
    keywords = 'utilities commands virtualenv',

    packages = list(find_packages(exclude=('tests', 'docs', 'docs.*'))),
    install_requires = 'virtualenv',
    scripts = ['bin/ve', 'bin/ve-extend', 'bin/ve-clone', 'bin/ve-init'],

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ]
)
