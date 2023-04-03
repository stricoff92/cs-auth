
from unittest import TestCase


class TestPatchesAreApplied(TestCase):

    def test_ldap3_patches_applied(self):
        # these imports will fail if the ldap3
        # package is not patched.
        from ldap3 import Server, Connection

    def test_global_packages_installed_for_ldif(self):
        # Global packages must be installed
        # for ldif module import to work.
        # Lets test that we can import.
        from ldif import LDIFParser
