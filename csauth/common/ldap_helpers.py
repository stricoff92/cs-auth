
""" This contains methods to
        > Connect to the LDAP server.
        > Manage .ldif files.
        > Perform basic CRUD operations against the LDAP server.
"""

from typing import Optional

from ldap3 import (
    Server as LDAPServer,
    Connection as LDAPConnection,
)

from applocals import (
    LDAP_SERVER_HOST,
    LDAP_ADMIN_DN,
    LDAP_ADMIN_PASSWORD_BASE64,
    LDAP_SERVER_DOMAIN_COMPONENTS,
)
from common import security_helpers


ALL_CLASSES_SEARCH_FILTER = '(objectClass=*)'


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

def add_base_dn(dn: str) -> str:
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

def get_posix_user_dn(cn: str) -> str:
    """ given a common name, create a propper dn for a posix user.
    """
    return add_base_dn(f'cn={cn},ou=people,ou=linuxlab')

def get_posix_group_dn(cn: str) -> str:
    """ given a common name, create a propper dn for a posix group.
    """
    return add_base_dn(f'cn={cn},ou=groups,ou=linuxlab')



# LDAP CRUD methods

def dn_exists(conn: LDAPConnection, dn: str, class_filter=None) -> bool:
    search_dn = add_base_dn(dn)
    return conn.search(
        search_dn,
        class_filter if class_filter else ALL_CLASSES_SEARCH_FILTER,
        paged_size=1,
    )

def posix_user_exists(conn: LDAPConnection, cn: str) -> bool:
    return dn_exists(conn, get_posix_user_dn(cn))

def posix_group_exists(conn: LDAPConnection, cn: str) -> bool:
    return dn_exists(conn, get_posix_group_dn(cn))
