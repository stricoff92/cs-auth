
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
from ldif import LDIFParser

from applocals import (
    LDAP_SERVER_HOST,
    LDAP_ADMIN_DN,
    LDAP_ADMIN_PASSWORD_BASE64,
)
from common import security_helpers


def new_server(host_name: Optional[str] = None) -> LDAPServer:
    ldap_host = host_name if host_name else LDAP_SERVER_HOST
    return LDAPServer(ldap_host)


def new_connection(
        server: Optional[LDAPServer] = None,
        admin_dn: Optional[str] = None,
        admin_pwd: Optional[str] = None,
        auto_bind: bool = True,
) -> LDAPConnection:
    return LDAPConnection(
        server if server else new_server(),
        admin_dn if admin_dn else LDAP_ADMIN_DN,
        admin_pwd if admin_pwd else security_helpers.b64decode(LDAP_ADMIN_PASSWORD_BASE64),
        auto_bind=auto_bind,
    )
