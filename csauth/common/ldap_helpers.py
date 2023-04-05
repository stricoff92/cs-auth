
""" This contains methods to
        > Connect to the LDAP server.
        > Manage .ldif files.
        > Perform basic CRUD operations against the LDAP server.
"""

from typing import Optional, Dict

from ldap3 import (
    Server as LDAPServer,
    Connection as LDAPConnection,
    ALL_ATTRIBUTES,
)
from ldap3.abstract.entry import Entry as LDAPEntry

from applocals import (
    LDAP_SERVER_HOST,
    LDAP_ADMIN_DN,
    LDAP_ADMIN_PASSWORD_BASE64,
    LDAP_SERVER_DOMAIN_COMPONENTS,
)
from common import security_helpers


# Search Filters.
ALL_CLASSES_SEARCH_FILTER = '(objectClass=*)'
POSIX_USER_SEARCH_FILTER = '(objectClass=posixAccount)'
POSIX_GROUP_SEARCH_FILTER = '(objectClass=posixGroup)'


# Errors.
class BaseLDAPCRUDError(Exception):
    pass

class LDAPObjectNotFoundError(Exception):
    pass

class PosixUserAlreadyExistsError(BaseLDAPCRUDError):
    pass

class PosixGroupAlreadyExistsError(BaseLDAPCRUDError):
    pass

class InvalidPosixUserAttributesError(BaseLDAPCRUDError):
    pass

class InvalidPosixGroupAttributesError(BaseLDAPCRUDError):
    pass


# LDAP factories # # #

def new_server(host_name: Optional[str] = None) -> LDAPServer:
    ''' Factory for creating a new Server instance
    '''
    ldap_host = host_name if host_name else LDAP_SERVER_HOST
    return LDAPServer(ldap_host)

def new_connection(
        server: Optional[LDAPServer] = None,
        admin_dn: Optional[str] = None,
        admin_pwd: Optional[str] = None,
        auto_bind: bool = True,
) -> LDAPConnection:
    ''' Factory for creating a new Connection instance.
    '''
    return LDAPConnection(
        server if server else new_server(),
        admin_dn if admin_dn else LDAP_ADMIN_DN,
        admin_pwd if admin_pwd else security_helpers.b64decode(LDAP_ADMIN_PASSWORD_BASE64),
        auto_bind=auto_bind,
    )


# distinguished/common name helpers # # #

def _add_base_domain_components_to_dn(dn: str) -> str:
    """ Check if a distinguished name is missing base dc parts.
        If dn is missing base dc parts add them.
    """
    cleaned_dn = dn.replace(' ', '')
    if not cleaned_dn:
        raise ValueError("expected a distinguished name")
    if cleaned_dn.endswith(',') or cleaned_dn.startswith(','):
        raise ValueError("passed dn has leading/trailing commas")

    if not cleaned_dn.endswith(LDAP_SERVER_DOMAIN_COMPONENTS):
        cleaned_dn += f',{LDAP_SERVER_DOMAIN_COMPONENTS}'
    return cleaned_dn


def _get_posix_user_dn(cn: str) -> str:
    """ given a common name, create a propper dn for a posix user.
    """
    return _add_base_domain_components_to_dn(
        f'cn={cn},ou=people,ou=linuxlab'
    )


def _get_posix_group_dn(cn: str) -> str:
    """ given a common name, create a propper dn for a posix group.
    """
    return _add_base_domain_components_to_dn(
        f'cn={cn},ou=groups,ou=linuxlab'
    )

def _ldap_entry_to_dict(entry: LDAPEntry) -> Dict:
    """ Convert an ldap entry to a python dict.
    """
    entry_dict = entry.entry_attributes_as_dict
    out = {}
    for k in entry_dict.keys():
        if not isinstance(entry_dict[k], list):
            raise NotImplementedError(
                f"expected a list, got {type(entry_dict[k])}"
            )
        elif len(entry_dict[k]) == 0:
            raise NotImplementedError("expected a length > 0")
        elif len(entry_dict[k]) == 1:
            # only 1 element in this list. Pop value and remove the list.
            out[k] = entry_dict[k][0]
        else:
            # This attribute is multi-valued, so leave it as a list.
            out[k] = entry_dict[k]
    return out


# LDAP CRUD methods

# Private methods.
def _dn_exists(conn: LDAPConnection, dn: str, class_filter=None) -> bool:
    return conn.search(
        dn,
        class_filter if class_filter else ALL_CLASSES_SEARCH_FILTER,
        paged_size=1,
    )


# Public methods.
def posix_user_exists(conn: LDAPConnection, cn: str) -> bool:
    return _dn_exists(
        conn,
        _get_posix_user_dn(cn),
        class_filter=POSIX_USER_SEARCH_FILTER,
    )


def posix_group_exists(conn: LDAPConnection, cn: str) -> bool:
    return _dn_exists(
        conn,
        _get_posix_group_dn(cn),
        class_filter=POSIX_GROUP_SEARCH_FILTER,
    )

def get_posix_user(
    conn: LDAPConnection,
    cn: str,
):
    found = conn.search(
        _get_posix_user_dn(cn),
        POSIX_USER_SEARCH_FILTER,
        paged_size=1,
        attributes=ALL_ATTRIBUTES,
    )
    if not found:
        raise LDAPObjectNotFoundError
    return _ldap_entry_to_dict(conn.entries[0])


def get_posix_group(
    conn: LDAPConnection,
    cn: str,
):
    found = conn.search(
        _get_posix_group_dn(cn),
        POSIX_GROUP_SEARCH_FILTER,
        paged_size=1,
        attributes=ALL_ATTRIBUTES,
    )
    if not found:
        raise LDAPObjectNotFoundError
    return _ldap_entry_to_dict(conn.entries[0])


def add_posix_user(
    conn: LDAPConnection,
    cn: str,
    attrs: Dict,
):
    if posix_user_exists(conn, cn):
        raise PosixUserAlreadyExistsError

    dn = _get_posix_user_dn(cn)


def add_posix_group(
    conn: LDAPConnection,
    cn: str,
    attrs: Dict,
):
    if posix_group_exists(conn, cn):
        raise PosixGroupAlreadyExistsError

    dn = _get_posix_user_dn(cn)
