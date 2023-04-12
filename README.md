# cs-auth

## slapd installation
```bash
sudo apt install slapd ldap-utils
sudo dpkg-reconfigure slapd
```

<hr>

## Python Management Suite Installation

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
<hr>

## Preprare for TLS

```bash
# setup directories
sudo -i;
mkdir /root/slapd/
mkdir /root/slapd/CA;
mkdir /root/slapd/CA/private;
mkdir /etc/ldap/certs
mkdir /etc/ldap/cacerts

# These instructions assume openssl will dump new certs to ./demoCA.
# You can confirm this by running:
openssl version -d
# then check the OPENSSLDIR/openssl.cnf file
cat OPENSSLDIR/openssl.cnf | grep dir
# dir		= ./demoCA		# Where everything is kept
# dir		= ./demoCA		# TSA root directory

mkdir /root/slapd/CA/demoCA
mkdir /root/slapd/CA/demoCA/newcerts/
touch /root/slapd/CA/demoCA/index.txt
echo 01 > /root/slapd/CA/demoCA/serial

```

```bash
# Create CA Certificate and key
cd /root/slapd/CA
# Create ca key
openssl genrsa -out ca.key 4096
# Create ca cert signed with ca key
openssl req -new -x509 -days 9999 -key ca.key -out ca.cert.pem

# Create Server TLS Certificate and key
# Replace MACHINE with server hostname.
# create private key
openssl genrsa -out private/MACHINE.key 4096

# create certificate signing request
openssl req -new -key private/MACHINE.key -out MACHINE.csr

# Create LDAP server certificate
openssl ca -days 9999 -keyfile ca.key -cert ca.cert.pem -in MACHINE.csr -out private/MACHINE.crt

# Move files to openldap directory
cp private/MACHINE.crt /etc/ldap/certs/
cp private/MACHINE.key /etc/ldap/certs/
cp ca.cert.pem /etc/ldap/certs/
chown -R openldap:openldap /etc/ldap/certs/
chown -R openldap:openldap /etc/ldap/cacerts/
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
./main load_tsv /path/to/posixUsers.tsv /path/to/posixGroups.tsv --password

# only import groups (/foo is a garbage input that is ignored but required)
./main load_tsv /foo /path/to/posixGroups.tsv --skipusers

```

## Using `ldapmodify` to configure slapd
```bash
# move template ldif files to gitignored directory for editing.
cp ldif_templates/*.ldif ldif/

# show config
sudo ldapsearch -Q -Y EXTERNAL -H ldapi:/// -b cn=config cn=config
# or
sudo ldapsearch -Q -Y EXTERNAL -H ldapi:/// -b cn=config -LLL

# Disable anonymous bind requests
sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f ldif/olcDisallows_bind_anon.ldif

# edit MACHINE value in ldif/olcTLSCACertificateFile_add.ldif
# then add CA Certificate to config
sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f ldif/olcTLSCACertificateFile_add.ldif

# edit MACHINE value in ldif/olcTLSCertificateFile_add.ldif
# then add TLS Certificate & Key to config
sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f ldif/olcTLSCertificateFile_add.ldif
```


## `ldapsearch` example usage
```bash
# Search using SASL auth as root
sudo ldapsearch -Q -Y EXTERNAL -H ldapi:/// -b 'cn=jonst,ou=people,ou=linuxlab,dc=cs,dc=hunter,dc=cuny,dc=edu'

# test search using anonymous simple auth
# (this should fail)
ldapsearch -b 'dc=cs,dc=hunter,dc=cuny,dc=edu' -H ldap://localhost -x
```
