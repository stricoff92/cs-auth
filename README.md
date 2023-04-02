# cs-auth

## Installation

README assumes you're using python 3.10. This readme should get updated in the future. Unfortunatly the python ldap client doesn't work out of the box with python3.10 until the library is patched. This may change with future updates. The patching that's required may also change in the future.


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

# Unfortunatly ldap3 library needs to be patched
packagedir=lib/python3.10/site-packages/ldap3 ./main patch_python_env
```
