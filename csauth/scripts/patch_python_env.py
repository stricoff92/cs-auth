
'''
    Python ldap client is not 100% compatable with python3.10.
    This script edits the library code such that it is compatable
    with python3.10.

    ldappackagedir environment variable must be set before running this script,
    for example:

    ldappackagedir=/home/jon/hunter-repos/cs-auth/env/lib/python3.10/site-packages/ldap3 ./main patch_python_env

'''


import os
import os.path
import sys

from common.command_runner import CommandRunner
from settings import BASE_DIR



def patch1(console, ldappackagedir):
    """
    rename env/lib/python3.X/site-packages/ldap3/strategy/async.py
        to env/lib/python3.X/site-packages/ldap3/strategy/async_.py

    then edit
    env/lib/python3.X/site-packages/ldap3/core/connection.py

    from ..strategy.async import AsyncStrategy
    changes to
    from ..strategy.async_ import AsyncStrategy
    """
    console.debug('starting patch 1')

    old_path = os.path.join(ldappackagedir, 'strategy/async.py')
    new_path = os.path.join(ldappackagedir, 'strategy/async_.py')
    console.debug(f"renaming '{old_path}' to '{new_path}'")

    if not os.path.exists(old_path):
        console.error(f"file does not exist: {old_path}")
        console.warning("skipping patch...")
        return

    CommandRunner(
        f'mv {old_path} {new_path}',
        run_now=True,
        raise_for_non_zero_exit_codes=True,
        get_output=False,
    )

    is_patched = False
    file_to_edit = os.path.join(ldappackagedir, 'core/connection.py')
    console.debug(f"editing '{file_to_edit}'")
    new_outlines = []
    with open(file_to_edit) as f:
        for ix, line in enumerate(f):
            if not is_patched and line.startswith('from ..strategy.async import AsyncStrategy'):
                new_outlines.append('from ..strategy.async_ import AsyncStrategy\n')
                is_patched = True
                console.debug(f"line {ix} edited")
            else:
                new_outlines.append(line)

    if is_patched:
        with open(file_to_edit, 'w') as f:
            for line in new_outlines:
                f.write(line)
        console.debug("SUCCESS: patch1 complete")
        return True
    else:
        console.debug("WARNING: patch1 did not find target line")

def patch2(console, ldappackagedir):
    """
    edit env/lib/python3.X/site-packages/ldap3/utils/ciDict.py

    change
    class CaseInsensitiveDict(collections.MutableMapping):
    to
    class CaseInsensitiveDict(collections.abc.MutableMapping):
    """
    console.debug('starting patch 2')

    file_to_edit = os.path.join(ldappackagedir, 'utils/ciDict.py')

    is_patched = False
    new_outlines = []
    console.debug(f"editing file '{file_to_edit}'")
    with open(file_to_edit) as f:
        for ix, line in enumerate(f):
            if not is_patched and line.startswith('class CaseInsensitiveDict(collections.MutableMapping):'):
                new_outlines.append('class CaseInsensitiveDict(collections.abc.MutableMapping):\n')
                is_patched = True
                console.debug(f"line {ix} edited")
            else:
                new_outlines.append(line)

    if is_patched:
        with open(file_to_edit, 'w') as f:
            for line in new_outlines:
                f.write(line)
        console.debug("SUCCESS: patch2 complete")
        return True
    else:
        console.debug("WARNING: patch2 did not find target line")


def main(console):
    # absolute path to package directory,
    # for example: '/home/jon/hunter-repos/cs-auth/env/lib/python3.10/site-packages/ldap3'
    ldappackagedir = os.environ['ldappackagedir']

    if not os.path.isdir(ldappackagedir):
        raise ValueError(f"directory does not exist: {ldappackagedir}")

    console.debug('LDAP client package directory: ' + ldappackagedir)
    patch_1_ok = patch1(console, ldappackagedir)
    patch_2_ok = patch2(console, ldappackagedir)

    if all([patch_1_ok, patch_2_ok]):
        console.debug("SUCCESS: all patches are applied")
        sys.exit(0)
    else:
        console.debug("WARNING: not all patches were applied")
        sys.exit(1)
