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

```bash
# copy ldif templates to a gitignored directory
cp ldif_templates/*.ldif ldif/
```

```bash
# show the config
sudo ldapsearch -Q -Y EXTERNAL -H ldapi:/// -b cn=config cn=config
```

<hr>

## Preprare for TLS

You should refer to distro specific documentation. The below is from https://ubuntu.com/server/docs/service-ldap-with-tls (ubuntu 22)

```bash
sudo -i

apt install gnutls-bin ssl-cert

# Create CA Certificate and key
sudo certtool --generate-privkey --bits 4096 --outfile /etc/ssl/private/slapd-cakey.pem
```

Create `/etc/ssl/ca.info`
```
cn = Hunter College
ca
cert_signing_key
expiration_days = 9999
```

Create self signed CA certificate
```bash
certtool --generate-self-signed \
--load-privkey /etc/ssl/private/slapd-cakey.pem \
--template /etc/ssl/ca.info \
--outfile /usr/local/share/ca-certificates/slapdca.crt

# collect the new CA cert
# this command creates symlink: (/etc/ssl/certs/slapdca.pem)
update-ca-certificates
```

Create `/etc/ssl/MACHINE.info`
```
organization = Hunter College
cn = MACHINE_FQDN_GOES_HERE
tls_www_server
encryption_key
signing_key
expiration_days = 9999

```

Create TLS key and certificate
```bash
# create private key
certtool --generate-privkey \
--bits 2048 \
--outfile /etc/ldap/MACHINE_slapd_key.pem

# create certificate
sudo certtool --generate-certificate \
--load-privkey /etc/ldap/MACHINE_slapd_key.pem \
--load-ca-certificate /etc/ssl/certs/slapdca.pem \
--load-ca-privkey /etc/ssl/private/slapd-cakey.pem \
--template /etc/ssl/MACHINE.info \
--outfile /etc/ldap/MACHINE_slapd_cert.pem

# Adjust permissions
sudo chgrp openldap /etc/ldap/MACHINE_slapd_key.pem
sudo chmod 0640 /etc/ldap/MACHINE_slapd_key.pem
```

```bash
# Apply slapd configuration changes

# replace MACHINE in ldif/set_tls_config.ldif then run
ldapmodify -Y EXTERNAL -H ldapi:// -f ldif/set_tls_config.ldif
```

Update slapd args in `/etc/default/slapd`. add `ldaps:///` to `SLAPD_SERVICES`, and then restart slapd with `systemctl restart slapd`

```bash
# optional: setup local port forwarding through jump box
ssh -L 1636:LDAPHOST:636 user@jumpbox.host

# now you connect to ldaps://localhost:1636
```

<hr>

## Apply Security Configuration Settings

```bash

# Disable anonymous bind requests
sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f ldif/olcDisallows_bind_anon.ldif

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

```

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

## `ldapsearch` example usage
```bash
# Search using SASL auth as root
sudo ldapsearch -Q -Y EXTERNAL -H ldapi:/// -b 'cn=jonst,ou=people,ou=linuxlab,dc=cs,dc=hunter,dc=cuny,dc=edu'

# test search using anonymous simple auth
# (this should fail)
ldapsearch -b 'dc=cs,dc=hunter,dc=cuny,dc=edu' -H ldap://localhost -x
```
