#### virtualenv-commands
#### Extended Environment API

### Copyright (c) 2009, Coptix, Inc.  All rights reserved.
### See the LICENSE file for license terms and warranty disclaimer.

"""ve -- virtualenv utilities"""

from __future__ import absolute_import
import os, re, contextlib
from . import script

__all__ = (
    'is_virtualenv', 'interpreter',
    'version', 'site_packages', 'sys_path',
    'create',
    'virtualenv', 'python',

    'has_extensions', 'extends_path', 'extends', 'write_extensions',
    'clone'
)


### Inspection

def is_virtualenv(ve):
    """Return True if the path ve exists and looks like a
    virtualenv."""

    return (
        os.path.exists(ve)
        and os.path.isfile(interpreter(ve))
    )

def interpreter(ve):
    """Return a path to the python interpreter for the virtualenv ve."""

    return os.path.join(ve, 'bin/python')

def version(ve):
    """Return the major.minor version of the python interpreter in
    virtualenv ve."""

    return python(ve, 'import sys; print "%d.%d" % sys.version_info[0:2]')

def site_packages(ve):
    """Return a path to the site-packages directory in virtualenv
    ve."""
    return os.path.join(ve, 'lib', 'python%s' % version(ve), 'site-packages')

def without_site_packages(path):
    """The inverse operation of site_packages()."""
    return path.rsplit('/lib/', 2)[0]

def sys_path(ve):
    return python(ve, 'import sys; print sys.path')


### Command execution

def create(ve):
    return virtualenv('--no-site-packages', '-q', ve)

def virtualenv(*args):
    """Run `virtualenv' with arguments args."""
    return script.python(script.which('virtualenv'), '-q', *args)

def python(ve, command):
    """Execute a simple python statement in the virtualenv
    interpreter.  Return the captured output."""

    assert is_virtualenv(ve)
    return script.capture(interpreter(ve), '-c', command).strip()


### Extensions

## Extending a virtual environment means "chaining" it to some other
## source environments.  Anything in the destination virtualenv
## overrides source virtualenvs.  This effect of extending one
## virtualenv with another is to append the source virtualenv
## site-packages to the sys.path of the destination virtualenv.

## For more information about sitecustomize.py, see the `site' module
## documentation.  Use sitecustomize.py instead of a `.pth' file since
## site.addsitedir() recursively expands the directory (processes any
## `.pth' files, runs its sitecustomize.py, etc).

EXTENDS = 'sitecustomize.py'

def has_extensions(ve):
    return is_virtualenv(ve) and os.path.exists(extends_path(ve))

def extends_path(ve):
    return os.path.join(site_packages(ve), EXTENDS)

def extends(ve):
    if has_extensions(ve):
        with extensions_file(ve) as port:
            return filter(None, (_extension_to_ve(l) for l in port.readlines()))
    return []

def write_extensions(ve, extends):
    with extensions_file(ve, 'w') as port:
        print >> port, 'import site'
        for source_ve in extends:
            print >> port, _ve_to_extension(source_ve)

def _ve_to_extension(ve):
    return 'site.addsitedir("%s")' % os.path.abspath(site_packages(ve))

_EXTENSION = re.compile('site\.addsitedir\("([^"]+)"\)')
def _extension_to_ve(ext):
    match = _EXTENSION.match(ext)
    return match and without_site_packages(match.group(1))

def extensions_file(ve, *args):
    assert is_virtualenv(ve)
    return contextlib.closing(open(extends_path(ve), *args))


### Clone

## Cloning a virtualenv means copying most of the source into the
## destination.  A little trickery happens in order to create all of
## the right paths in the destination correctly.  The basic strategy
## is to create the new virtualenv, move it out of the way, copy the
## source virtualenv, then overlay the newly-created virtualenv's bin
## directory onto the copy of the source.

CLONE_OVERWRITE = ('bin', )

def clone(source, dest):

    with script.tempdir(prefix='ve-clone-') as temp:
        new_ve = os.path.join(temp, 'new')
        old_ve = os.path.join(temp, 'old')

        ## Do this transactionally.  If something goes wrong, leave
        ## the filesystem as it was.
        if os.path.exists(dest):
            script.move(dest, old_ve)

        try:
            ## 1. Create the new virtualenv in the correct location.
            create(dest)

            ## 2. Move it out of the way.
            script.move(dest, new_ve)

            ## 3. Copy the source virtualenv to the correct
            ## destination path.
            script.copy(source, dest)

            ## 4. Copy the necessary parts of the new virtualenv over the
            ## copied source.
            script.overwrite(
                (os.path.join(new_ve, rel) for rel in CLONE_OVERWRITE),
                dest
            )
        except Exception:
            ## Something went wrong.  Put the old virtualenv back.
            if os.path.exists(dest):
                script.remove(dest)
            if os.path.exists(old_ve):
                script.move(old_ve, dest)
            raise
