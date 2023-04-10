# cs-auth

## Installation

README assumes you're using python 3.10. This readme should get updated in the future. The python ldap client doesn't work out of the box with python3.10 until the library is patched. This may change with future updates. The patching that's required may also change in the future.


```bash
# create applocals file
touch csauth/applocals.py
chmod 600 csauth/applocals.py
```

Example `applocals.py` file
```
LDAP_SERVER_HOST = 'cs-auth'
LDAP_SERVER_DOMAIN_COMPONENTS = 'dc=cs,dc=hunter,dc=cuny,dc=edu'
LDAP_ADMIN_DN = f'cn=admin,{LDAP_SERVER_DOMAIN_COMPONENTS}'
LDAP_ADMIN_PASSWORD_BASE64 = 'BASE_64_ENCODED_PW_GOES_HERE'
```


```bash
# Install needed packages.

sudo apt-get install python3.10-venv python3-dev libsasl2-dev libldap2-dev libssl-dev libldb-dev libldap2-dev
```

```bash
# Build and patch python environment.

cd cs-auth/
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# ldap3 library needs to be patched for python3.10
ldappackagedir=/home/jon/hunter-repos/cs-auth/env/lib/python3.10/site-packages/ldap3 ./main patch_python_env
```

```bash
# Run unit tests

./test
```

```bash
# New TLS Certificate
sudo -i
cd ~
mkdir certs; cd certs;
openssl req -new -newkey rsa:4096 -x509 -sha256 -days 9999 -nodes -out OpenLDAPServer.crt -keyout OpenLDAPServer.key
```


<hr>

## Script Usage

```bash
# encode text to base64
./main base_64_encode myawesomepassword

# Create interchange formatted data.
# Data is exported to the csauth/outputs directory
sudo ./main unix_to_tsv /etc/passwd /etc/shadow /etc/group

# import interchange formatted users & groups
./main load_tsv /path/to/posixUsers.tsv /path/to/posixGroups.tsv

# import interchange formatted users & groups
# use a single password for newly added users.
./main load_tsv /path/to/posixUsers.tsv /path/to/posixGroups.tsv --password myawesomepassword

# only import groups (/foo is a garbage input that is ignored but required)
./main load_tsv /foo /path/to/posixGroups.tsv --skipusers

```

## Using `ldapmodify` to configure slapd
```bash
# show global config
sudo ldapsearch -Q -Y EXTERNAL -H ldapi:/// -b cn=config -LLL

# Disable anonymous bind requests
sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f ldif/olcDisallows_bind_anon.ldif
```


## `ldapsearch` example usage
```bash
# Search using SASL auth as root
sudo ldapsearch -Q -Y EXTERNAL -H ldapi:/// -b 'cn=jonst,ou=people,ou=linuxlab,dc=cs,dc=hunter,dc=cuny,dc=edu'

# test search using anonymous simple auth
# (this should fail)
ldapsearch -b 'dc=cs,dc=hunter,dc=cuny,dc=edu' -H ldap://localhost -x
```
