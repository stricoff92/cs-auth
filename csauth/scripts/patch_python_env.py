
import os
import os.path
import sys

from settings import BASE_DIR

def patch1(env_dir):
    """
    rename env/lib/python3.10/site-packages/ldap3/strategy/async.py
        to env/lib/python3.10/site-packages/ldap3/strategy/async_.py

    then edit
    env/lib/python3.10/site-packages/ldap3/core/connection.py

    from ..strategy.async import AsyncStrategy
    changes to
    from ..strategy.async_ import AsyncStrategy
    """

    old_path = os.path.join(env_dir, 'lib/python3.10/site-packages/ldap3/strategy/async.py')
    new_path = os.path.join(env_dir, 'lib/python3.10/site-packages/ldap3/strategy/async_.py')
    os.system(f'mv {old_path} {new_path}')

    is_patched = False
    file_to_edit = os.path.join(env_dir, 'lib/python3.10/site-packages/ldap3/core/connection.py')
    new_outlines = []
    with open(file_to_edit) as f:
        for line in f:
            if not is_patched and line.startswith('from ..strategy.async import AsyncStrategy'):
                new_outlines.append('from ..strategy.async_ import AsyncStrategy\n')
                is_patched = True
            else:
                new_outlines.append(line)

    if is_patched:
        with open(file_to_edit, 'w') as f:
            for line in new_outlines:
                f.write(line)
        print("SUCCESS: patch1 complete")
        return True
    else:
        print("WARNING: patch1 did not find target line")

def patch2(env_dir):
    """
    edit env/lib/python3.10/site-packages/ldap3/utils/ciDict.py

    change
    class CaseInsensitiveDict(collections.MutableMapping):
    to
    class CaseInsensitiveDict(collections.abc.MutableMapping):
    """
    file_to_edit = os.path.join(env_dir, 'lib/python3.10/site-packages/ldap3/utils/ciDict.py')

    is_patched = False
    new_outlines = []
    with open(file_to_edit) as f:
        for line in f:
            if not is_patched and line.startswith('class CaseInsensitiveDict(collections.MutableMapping):'):
                new_outlines.append('class CaseInsensitiveDict(collections.abc.MutableMapping):\n')
                is_patched = True
            else:
                new_outlines.append(line)

    if is_patched:
        with open(file_to_edit, 'w') as f:
            for line in new_outlines:
                f.write(line)
        print("SUCCESS: patch2 complete")
        return True
    else:
        print("WARNING: patch2 did not find target line")


def main():
    env_dir = os.path.join(BASE_DIR, '..', 'env')
    print('pyenv directory: ' + env_dir)
    patch_1_ok = patch1(env_dir)
    patch_2_ok = patch2(env_dir)

    if all([patch_1_ok, patch_2_ok]):
        print("SUCCESS: all patches are applied")
        sys.exit(0)
    else:
        print("WARNING: not all patches were applied")
        sys.exit(1)
