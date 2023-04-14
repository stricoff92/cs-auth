
""" This contains methods to
        > Connect to the LDAP server.
        > Manage .ldif files.
        > Perform basic CRUD operations against the LDAP server.
"""

import re
import ssl
from typing import (
    Optional,
    Dict,
    List,
)

from ldap3 import (
    Server as LDAPServer,
    Connection as LDAPConnection,
    Tls,
    ALL_ATTRIBUTES,
    MODIFY_REPLACE,
)
from ldap3.abstract.entry import Entry as LDAPEntry

from applocals import (
    LDAP_SERVER_HOST,
    LDAP_ADMIN_DN,
    LDAP_ADMIN_PASSWORD_BASE64,
    LDAP_SERVER_DOMAIN_COMPONENTS,
    LDAP_USE_SSL,
    LDAP_SERVER_CA_CERT,
)
from common import security_helpers



ALL_CLASSES_SEARCH_FILTER = '(objectClass=*)'
POSIX_USER_SEARCH_FILTER = '(objectClass=posixAccount)'
POSIX_GROUP_SEARCH_FILTER = '(objectClass=posixGroup)'
IP_HOST_SEARCH_FILTER = '(objectClass=ipHost)'

POSIX_USER_CLASS_LIST = [
    'account', 'posixAccount', 'shadowAccount', 'top',
]
POSIX_GROUP_CLASS_LIST = [
    'posixGroup', 'top',
]
IP_HOST_CLASS_LIST = [
    'device', 'ipHost', 'top',
]

# Errors.
class LDAPCRUDError(Exception):
    pass

class LDAPObjectNotFoundError(Exception):
    pass

class PosixUserAlreadyExistsError(LDAPCRUDError):
    pass

class PosixGroupAlreadyExistsError(LDAPCRUDError):
    pass

class InvalidPosixUserAttributesError(LDAPCRUDError):
    pass

class InvalidPosixGroupAttributesError(LDAPCRUDError):
    pass

class IPHostAlreadyExistsError(LDAPCRUDError):
    pass


LDAP_URI_PATTERN = re.compile(r'^ldaps?\:\/\/')
LDAP_CLEARTEXT_URI_PROTOCOL = 'ldap://'
LDAP_SSL_URI_PROTOCOL = 'ldaps://'

# LDAP client factories # # #
def new_server(
    host_name: Optional[str] = None,
    use_ssl: bool = None,
) -> LDAPServer:
    ''' Factory for creating a new Server instance
    '''
    ldap_host = host_name if host_name else LDAP_SERVER_HOST
    if LDAP_URI_PATTERN.match(ldap_host):
        raise ValueError("passed uri includes protocol. Do not pass protocol")

    if use_ssl:
        return LDAPServer(
            LDAP_SSL_URI_PROTOCOL + ldap_host,
            port=636,
            tls=Tls(
                ca_certs_file=LDAP_SERVER_CA_CERT,
                validate=ssl.CERT_REQUIRED,
            ),
        )
    else:
        return LDAPServer(LDAP_CLEARTEXT_URI_PROTOCOL + ldap_host)

def new_connection(
        server: Optional[LDAPServer] = None,
        admin_dn: Optional[str] = None,
        admin_pwd: Optional[str] = None,
        auto_bind: bool = True,
        use_ssl: Optional[bool] = None,
) -> LDAPConnection:
    ''' Factory for creating a new Connection instance.
    '''
    if server is not None and use_ssl is not None:
        raise ValueError("invalid arg combination passed")

    use_ssl = use_ssl if use_ssl is not None else LDAP_USE_SSL
    return LDAPConnection(
        server if server else new_server(use_ssl=use_ssl),
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

def _get_ip_host_dn(cn: str) -> str:
    return _add_base_domain_components_to_dn(
        f'cn={cn},ou=hosts,ou=linuxlab'
    )

# Low Level LDAP CRUD methods

def _dn_exists(conn: LDAPConnection, dn: str, class_filter=None) -> bool:
    return conn.search(
        dn,
        class_filter if class_filter else ALL_CLASSES_SEARCH_FILTER,
        paged_size=1,
    )


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

def ip_host_exists(conn: LDAPConnection, cn: str) -> bool:
    return _dn_exists(
        conn,
        _get_ip_host_dn(cn),
        class_filter=IP_HOST_SEARCH_FILTER,
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
        elif (
            len(entry_dict[k]) == 1
            and (
                'posixGroup' not in entry_dict['objectClass']
                or k != 'memberUid'
            )
        ):
            # only 1 element in this list. Pop value and remove the list
            # if it's not a posixGroup::memberUid attribute
            out[k] = entry_dict[k][0]
        else:
            # This attribute is multi-valued, so leave it as a list.
            out[k] = entry_dict[k]
    return out

def validate_response_is_success(resp: Dict):
    if resp.get('description') == 'success':
        return
    raise LDAPCRUDError

def get_posix_user(
    conn: LDAPConnection,
    cn: str,
) -> Dict:
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
) -> Dict:
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
    conn.add(
        dn,
        POSIX_USER_CLASS_LIST,
        attrs,
    )
    return conn.result


def add_posix_group(
    conn: LDAPConnection,
    cn: str,
    attrs: Dict,
):
    if posix_group_exists(conn, cn):
        raise PosixGroupAlreadyExistsError

    dn = _get_posix_group_dn(cn)
    conn.add(
        dn,
        POSIX_GROUP_CLASS_LIST,
        attrs,
    )
    return conn.result


def set_posix_group_members(
    conn: LDAPConnection,
    cn: str,
    memberUids: List[str],
):
    dn = _get_posix_group_dn(cn)
    changes = {
        'memberUid': [(MODIFY_REPLACE, memberUids,)],
    }
    conn.modify(dn, changes)
    return conn.result


def sync_user_password(
    conn: LDAPConnection,
    cn: str,
    userPassword: bytes
):
    dn = _get_posix_user_dn(cn)
    changes = {
        'userPassword': [(MODIFY_REPLACE, [userPassword],)],
    }
    conn.modify(dn, changes)
    return conn.result

def add_ip_host(
    conn: LDAPConnection,
    cn: str,
    ipv4: str
):
    if ip_host_exists(conn, cn):
        raise IPHostAlreadyExistsError
    dn = _get_ip_host_dn(cn)
    entry = create_ip_host_entry(cn, ipv4)
    conn.add(
        dn,
        IP_HOST_CLASS_LIST,
        entry,
    )
    return conn.result

# LDAP entry attribute factories # # #
def create_posix_user_entry_dict(
        username: str,
        uidNumber: str,
        gidNumber: int,
        fullname: str,
        homeDirectory: str,
        hashedUserPassword: bytes,
        loginShell,
) -> Dict:
    return {
        'cn': username,
        'uid': username,
        'uidNumber': uidNumber,
        'gidNumber': gidNumber,
        'homeDirectory': homeDirectory,
        'loginShell': loginShell,
        'gecos': fullname,
        'userPassword': hashedUserPassword,
        'shadowLastChange': 0,
        'shadowMax': 99999,
        'shadowWarning': 720,
    }

def create_posix_group_entry_dict(
    name: str,
    gidNumber: int,
    members: List[str],
) -> Dict:
    entry = {
        'cn': name,
        'gidNumber': gidNumber,
    }
    if len(members):
        entry['memberUid'] = members
    return entry

def create_ip_host_entry(cn: str, ipv4: str) -> Dict:
    return {
        'cn': cn,
        'ipHostNumber': ipv4,
    }
