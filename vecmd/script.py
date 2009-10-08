#### virtualenv-commands
#### Scripting Utilities

### Copyright (c) 2009, Coptix, Inc.  All rights reserved.
### See the LICENSE file for license terms and warranty disclaimer.

"""script -- Utilities for writing scripts."""

from __future__ import absolute_import
import os, sys, subprocess, tempfile, contextlib, optparse, inspect


### Options and script execution

def begin(proc, require=None, usage=None, description=None, options=None):
    """Begin executing a command-line python script.

    Example:

    def main(foo, bar):
        # main program

    if __name__ = '__main__':
        begin(main, usage="usage: %prog foo bar")
    """
    parser = optparse.OptionParser(usage, description=description)
    parser.disable_interspersed_args()
    if options:
        for (args, kwargs) in options:
            parser.add_option(*args, **kwargs)

    ## The number of required arguments is the same as the number of
    ## normal arguments to proc.  If proc accepts varargs, this
    ## command is nary.
    spec = inspect.getargspec(proc)
    nary = spec[1] is not None
    if require is None:
        require = len(spec[0]) - (len(spec[3]) if spec[3] else 0)

    (options, args) = parser.parse_args()

    arity = len(args)
    if arity < require:
        parser.error(
            'not enough arguments: %d expected, got %d' % (require, arity)
        )
    elif not nary and arity > require:
        parser.error(
            'too many arguments: %d expected, got %d' % (require, arity)
        )

    sys.exit(proc(*args, **options.__dict__))

def option(*args, **kwargs):
    """Encapsulate the arguments to OptionParser.add_option() for
    later use."""
    return (args, kwargs)


### Utilities

def log(*args):
    """Print a log message to STDERR."""

    print >> sys.stderr, ' '.join(str(a) for a in args)

def choose(prompt, choices='yn', default='n'):
    """Present the user with a yes/no prompt.  Return True if the user
    chooses "yes"."""

    compact = ''.join(c.upper() if c == default else c for c in choices)
    prompt = '%s [%s]: ' % (prompt, compact)

    value = ''
    while True:
        value = raw_input(prompt).strip().lower() or default
        if value in choices:
            break
        print 'Invalid choice.'

    return value

def confirm(prompt, default='n'):
    return choose(prompt, default=default) == 'y'

@contextlib.contextmanager
def tempdir(*args, **kwargs):
    """Produce a context in which a temporary directory exists.
    Destroy it when the context is exited."""

    path = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield path
    finally:
        remove(path)


### Subprocess

def must(*args):
    ## FIXME: For some reason check_call() doesn't execute args as a
    ## tuple.
    cmd = join_args(*args)
    # log('+', cmd)
    return subprocess.check_call(cmd, shell=True)

def capture(*args):
    return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

def capture_stderr(*args):
    return subprocess.Popen(args, stderr=subprocess.PIPE).communicate()[1]

def join_args(*args):
    from pipes import quote
    return ' '.join(quote(a) for a in args)

## Commands

def overwrite(source, dest):
    """Write source files over dest.  The destination is not deleted
    first, so the result is to merge source files into dest."""

    args = [source] if isinstance(source, basestring) else list(source)
    args.append(dest)

    return must('rsync', '-aq', *args)

def which(*args):
    return capture('which', *args).strip()

def move(*args):
    return must('mv', *args)

def copy(*args):
    return must('cp', '-Rp', *args)

def remove(*paths):
    return must('rm', '-rf', *paths)

def python(*args):
    return must(current_python_interpreter(), *args)

def current_python_interpreter():
    ## Note: This is kludge; what's a better way to find the "current"
    ## python interpreter?

    ## If this script is being executed directly, use which() to find
    ## the python interpreter.  Otherwise, assume the script is being
    ## run through a python interpreter directly; look for the
    ## interpreter in the environment.

    path = os.environ['_']
    if os.path.basename(path).startswith('python'):
        return path
    else:
        return which('python')
