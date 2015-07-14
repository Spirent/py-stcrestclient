"""
Install a new StcPython.py client module to enable use of STC ReST API.

This script replaces StcPython.py with new module that loads ReST API client
adapter module or legacy client module, depending on whether or not the
environment variable STC_REST_API is set to a non-empty value.  If there is an
existing legacy StcPython.py, it is renamed and will be used if STC_REST_API is
not set.

"""
from __future__ import absolute_import
from __future__ import print_function

import os


py_code = """# Import client BLL module or ReST API adapter if STC_REST_API=1
from __future__ import print_function
import os

if os.environ.get('STC_REST_API'):
    try:
        from stcrestclient.stcpythonrest import StcPythonRest as StcPython
    except ImportError:
        raise ImportError('Unable to import stcrestclient.  To install '
                          'latest: pip install stcrestclient --upgrade')
else:
    try:
        from stcpythonbll import StcPython
    except ImportError:
        raise ImportError(
            'Unable to import client BLL module.  If STC not installed, then '
            'clients must use ReST API.  To enable, set: STC_REST_API=1')

"""


if __name__ == '__main__':
    orig_py = 'StcPython.py'
    if os.path.isfile(orig_py):
        is_orig = True
        with open(orig_py) as script:
            if script.read().find('STC_REST_API') != -1:
                # File contains 'STC_REST_API' so it is not the original.
                is_orig = False
        if is_orig:
            # If this is the original StcPython.py, then rename it.
            dst = 'stcpythonbll.py'
            os.rename(orig_py, dst)
            print('===> renamed', orig_py, 'to', dst)
    else:
        print(
            'Did not find %s to replace in the current directory' % (orig_py,),
            '',
            'If you want to adapt an STC installation to use either ReST or',
            'legacy API, depending on STC_REST_API being set or not, run this',
            'script in your STC install directory.', '', sep='\n')

    with open(orig_py, 'w') as outf:
        outf.write(py_code)

    print('===> created new', orig_py)
    print('To enable ReST API in your Python STC automation scripts, set '
          'the environment', 'variable: STC_REST_API=1', sep='\n')
