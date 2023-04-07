
from unittest import TestCase
from unittest.mock import MagicMock

from common import ldap_helpers as ldap


class TestLDAPHelpers(TestCase):

    def test_single_attributes_are_popped_from_list(self):
        entry = ldap._ldap_entry_to_dict(
            MagicMock(entry_attributes_as_dict={
                'objectClass':['top', 'posixAccount'],
                'attr1': ['foo'],
                'attr2': ['lorum', 'ipsum'],
            })
        )
        self.assertEqual(entry, {
            'objectClass':['top', 'posixAccount'],
            'attr1': 'foo', # single value popped from list
            'attr2': ['lorum', 'ipsum'],
        })

    def test_single_posixGroup_memberUid_attribute_is_not_popped_from_list(self):
        entry = ldap._ldap_entry_to_dict(
            MagicMock(entry_attributes_as_dict={
                'objectClass':['top', 'posixGroup'],
                'attr1': ['foo'],
                'attr2': ['lorum', 'ipsum'],
                'memberUid': ['derpy'],
            })
        )
        self.assertEqual(entry, {
                'objectClass':['top', 'posixGroup'],
                'attr1': 'foo', # single value popped from list
                'attr2': ['lorum', 'ipsum'],
                'memberUid': ['derpy'], # single value not popped from list
        })
