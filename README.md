# Unix to OpenLDAP Migration Tool

## What is this Repo?
 - A readme which details how to install and configure `openLDAP` and `sssd`
 - A Python CLI program that:
   - migrates data from a UNIX backend to an openLDAP backend
   - provides management scripts for doing CRUD operations on OpenLDAP

<hr>

## Python Management Suite Installation


```bash
# create applocals file
touch csauth/applocals.py
chmod 600 csauth/applocals.py
```

Example `applocals.py` file
```python
LDAP_SERVER_HOST = 'cs-auth'
LDAP_SERVER_DOMAIN_COMPONENTS = 'dc=cs,dc=hunter,dc=cuny,dc=edu'
LDAP_ADMIN_DN = f'cn=admin,{LDAP_SERVER_DOMAIN_COMPONENTS}'
LDAP_ADMIN_PASSWORD_BASE64 = 'BASE_64_ENCODED_PW_GOES_HERE'
LDAP_USE_SSL = True
LDAP_SERVER_CA_CERT = '/usr/local/share/ca-certificates/slapdca.crt'

# These 2 files get generated later in the guide
LDAP_CLIENT_TLS_CERT = '/etc/ldap/CLIENT_MACHINE_cert.pem'
LDAP_CLIENT_TLS_KEY = '/etc/ldap/CLIENT_MACHINE_key.pem'
```



```bash
# Install needed packages.

sudo apt-get install python3.10-venv python3-dev libsasl2-dev libldap2-dev libssl-dev libldb-dev libldap2-dev
```

```bash
# Build python environment.

cd cs-auth/
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

```bash
# Run unit tests

./test
```

<hr>

## slapd installation
```bash
sudo apt install slapd ldap-utils
sudo dpkg-reconfigure slapd
```

## Setup TLS

You should refer to distro specific documentation. The below is from https://ubuntu.com/server/docs/service-ldap-with-tls (ubuntu 22)

```bash
# copy ldif templates to a gitignored directory
cp ldif_templates/*.ldif ldif/
```

```bash
# show the config
sudo ldapsearch -Q -Y EXTERNAL -H ldapi:/// -b cn=config cn=config
```


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

# copy `/usr/local/share/ca-certificates/slapdca.crt` onto a flash drive. ldaps:// clients will need to load this CA certificate.
cp /usr/local/share/ca-certificates/slapdca.crt /media/USER/myflashdrive
```

Create `/etc/ssl/SERVER_MACHINE.info`
```
organization = Hunter College
cn = SERVER_MACHINE_FQDN_GOES_HERE
tls_www_server
encryption_key
signing_key
expiration_days = 9999

```

### Create TLS key and certificate for SERVER
```bash
# create private key
certtool --generate-privkey \
--bits 2048 \
--outfile /etc/ldap/SERVER_MACHINE_slapd_key.pem

# create certificate
sudo certtool --generate-certificate \
--load-privkey /etc/ldap/SERVER_MACHINE_slapd_key.pem \
--load-ca-certificate /etc/ssl/certs/slapdca.pem \
--load-ca-privkey /etc/ssl/private/slapd-cakey.pem \
--template /etc/ssl/SERVER_MACHINE.info \
--outfile /etc/ldap/SERVER_MACHINE_slapd_cert.pem

# Adjust permissions
sudo chgrp openldap /etc/ldap/SERVER_MACHINE_slapd_key.pem
sudo chmod 0640 /etc/ldap/SERVER_MACHINE_slapd_key.pem
```

```bash
# Apply slapd configuration changes

# replace MACHINE in ldif/set_tls_config.ldif then run
ldapmodify -Y EXTERNAL -H ldapi:// -f ldif/set_tls_config.ldif
```

Update slapd args in `/etc/default/slapd`. add `ldaps:///` to `SLAPD_SERVICES`, and then restart slapd with `systemctl restart slapd`


### Create TLS key and certificate for CLIENT(s)

```bash
# Create a directory on the SERVER which will hold minted client keys & certs
sudo -i
mkdir /root/client-certs && cd /root/client-certs
chmod 700 /root/client-certs
```

Create `CLIENT_MACHINE.info`
```
organization = Hunter College
cn = MACHINE_FQDN_GOES_HERE
tls_www_server
encryption_key
signing_key
expiration_days = 9999
```

```bash
# create private key
certtool --generate-privkey \
--bits 2048 \
--outfile CLIENT_MACHINE_key.pem

# create certificate
sudo certtool --generate-certificate \
--load-privkey CLIENT_MACHINE_key.pem \
--load-ca-certificate /etc/ssl/certs/slapdca.pem \
--load-ca-privkey /etc/ssl/private/slapd-cakey.pem \
--template CLIENT_MACHINE.info \
--outfile CLIENT_MACHINE_cert.pem


# copy keys over to client machine
cp CLIENT_MACHINE_key.pem /media/USER/flash-drive/
cp CLIENT_MACHINE_cert.pem /media/USER/flash-drive/
# instructions below assume these 2 keys will be placed on the client machines:
# /etc/ldap/CLIENT_MACHINE_cert.pem
# /etc/ldap/CLIENT_MACHINE_key.pem

# make sure these permissions are set on the client machine:
chown root:root /etc/ldap/CLIENT_MACHINE_cert.pem
chmod 644 /etc/ldap/CLIENT_MACHINE_cert.pem

chown root:root /etc/ldap/CLIENT_MACHINE_key.pem
chmod 600 /etc/ldap/CLIENT_MACHINE_key.pem
```

<hr>
Helper commands

```bash
# setup local port forwarding for ldap://
ssh -L 1389:LDAPHOST:389 user@jumpbox.host

# setup local port forwarding for ldaps://
ssh -L 1636:LDAPHOST:636 user@jumpbox.host

```

<hr>


## Apply Security configurations to SLAPD

```bash
# Disable anonymous bind requests
suod ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f ldif/olcDisallows_bind_anon.ldif

# Require valid TLS certs from the client
sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f ldif/olcTLSVerifyClient_demand.ldif
```

Verify Access Controls

```bash
# Find database config (for example olcDatabase={1}mdb)
ldapsearch  -Y EXTERNAL -H ldapi:/// -b cn=config dn
# View oldAccess config entries for olcDatabase={1}mdb
ldapsearch  -Y EXTERNAL -H ldapi:/// -b cn=config 'olcDatabase={1}mdb'
# Default access controls are suitable:
# olcAccess: {0}to attrs=userPassword by self write by anonymous auth by * none
# olcAccess: {1}to attrs=shadowLastChange by self write by * read
# olcAccess: {2}to * by * read

```

## Apply Security configurations to LDAP server OS (Ubuntu)

```bash
sudo -i

# view network firewall settings
ufw status verbose

# setup network firewall, allow ssh/sftp
ufw enable && ufw allow 22

# By default we'll block all incoming traffic
sudo ufw default deny incoming

# allow localhost to access ldap in the clear
ufw allow from 127.0.0.1 to 127.0.0.1 port 389

# allow subnet ipv4 traffic to access ldap over TLS
ufw allow from 146.95.214.0/24 proto tcp to 0.0.0.0/0 port 636
ufw allow from 127.0.0.1 to 127.0.0.1 port 636

```

## Test Server Security Settings

```bash
# expected results:
# ⌛❌ = hangs
# 💀❌ = crashes
#   ✅ = works

# Search using SASL as root on SERVER (talking to localhost)
  ✅ sudo ldapwhoami -Q -Y EXTERNAL -H ldapi:///

# search using anonymous simple auth fails on SERVER and CLIENT
💀❌ ldapwhoami -H ldap://localhost -x
💀❌ ldapwhoami -H ldaps://localhost -x
💀❌ ldapwhoami -H ldap://MACHINE.cs.hunter.cuny.edu -x

# ldaps works on the CLIENT
  ✅ ldapwhoami -x -H ldaps://MACHINE.cs.hunter.cuny.edu -D 'cn=admin,dc=cs,dc=hunter,dc=cuny,dc=edu' -W

# ldap in the clear only works on the SERVER (talking to localhost).
  ✅ ldapwhoami -x -H ldap:/// -D 'cn=admin,dc=cs,dc=hunter,dc=cuny,dc=edu' -W

# ldap in the clear fails on the client.
⌛❌ ldapwhoami -x -H ldap://MACHINE.cs.hunter.cuny.edu -D 'cn=admin,dc=cs,dc=hunter,dc=cuny,dc=edu' -W
```

<hr>

## Setup LDAP Client

You should refer to distro specific documentation. The below is from https://ubuntu.com/server/docs/service-sssd-ldap (ubuntu 22)

```bash
sudo -i
apt install sssd-ldap
touch /etc/sssd/sssd.conf
chown root:root /etc/sssd/sssd.conf
chmod 600 /etc/sssd/sssd.conf
```

add data to `/etc/sssd/sssd.conf`:
```
[sssd]
config_file_version = 2
domains = MACHINE.cs.hunter.cuny.edu
services = nss,pam

[domain/MACHINE.cs.hunter.cuny.edu]
id_provider = ldap
auth_provider = ldap
ldap_uri = ldaps://MACHINE.cs.hunter.cuny.edu
cache_credentials = True
ldap_search_base = ou=linuxlab,dc=cs,dc=hunter,dc=cuny,dc=edu
ldap_tls_cacert = /usr/local/share/ca-certificates/slapdca.crt
ldap_tls_reqcert = hard
ldap_tls_cert = /etc/ldap/CLIENT_MACHINE_cert.pem
ldap_tls_key = /etc/ldap/CLIENT_MACHINE_key.pem
```

```bash
# start daemon
sudo systemctl start sssd.service
```

edit /etc/nsswitch.conf. add 'sss' as a hosts provider
```
# /etc/nsswitch.conf
...
hosts:          files mdns4_minimal [NOTFOUND=return] dns sss
```

```bash
# restart daemon
sudo systemctl restart sssd.service
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

## `ldapsearch` example usage
```bash
# Search using SASL as root on ldap server
sudo ldapsearch -Q -Y EXTERNAL -H ldapi:/// -b 'cn=jonst,ou=people,ou=linuxlab,dc=cs,dc=hunter,dc=cuny,dc=edu'

# ldaps search works locally and on the subnet.
ldapsearch -x -H ldaps://MACHINE.cs.hunter.cuny.edu -D 'cn=admin,dc=cs,dc=hunter,dc=cuny,dc=edu' -W -b 'cn=jonst,ou=people,ou=linuxlab,dc=cs,dc=hunter,dc=cuny,dc=edu'

```
