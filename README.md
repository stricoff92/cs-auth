# cs-auth

## Installation

This project uses python 3.10

```bash
sudo apt-get install python3.10-venv python3-dev libsasl2-dev libldap2-dev libssl-dev libldb-dev libldap2-dev
```

```bash
cd cs-auth/
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# Unfortunatly ldap3 library needs to be patched
./main patch_python_env
```
