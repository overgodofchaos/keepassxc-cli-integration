# keepassxc_cli_integration



*CLI and Python integration for KeepassXC GUI.*

---


# CLI

---
- kpx
    - get
        - login
            - {{url}} (Get login for the specified URL from open databases.)
        - password
            - {{url}} (Get password for the specified URL from open databases.)
        - \--name (Specify the name of the entry in the database. Required if the URL has multiple entries.)
        - \--bat (Escape output to use BAT.)
    - associate
        - add (Default. Create an association with the CURRENT ACTIVE database.)
        - delete
            - {{select}} (Default: "current". Delete the selected association. You can specify the association name as either "all" or "current".)
        - show (Show all saved associations.)

---

# Python

--- 

The keepassxc_cli_integration.kpx module provides similar functions for use directly in Python.

---

*Notes:*
- **KeepassXC-GUI !!!MUST!!! have browser integration enabled.**
- *The association is carried out only with the active (and not with all open) databases. In order to receive information from all open databases, you must first carry out an association with each of them.*
- *Intended for Windows. May or may not work on Linux.*
- *Due to limitations of KeepassXC-GUI, it is possible to retrieve records from databases only by URL. The URL field **can be** written in the database without http(s):\\ and **can** also be specified without http(s):\\ in CLI\Python to retrieve data.*

---

# Example

---

```powershell
# example.ps1
$VeraCrypt = "C:\Program Files\VeraCrypt\VeraCrypt.exe"
$password = kpx get passoword example-vault

& $VeraCrypt /volume "C:\example\vault.hc" /letter Y /password $password /b /q
```

# Installation

1. pip / pipx
```
pip (or pipx) install keepassxc_cli_integration
```
2. git
```
git clone https://github.com/overgodofchaos/keepassxc_cli_integration.git
cd keepassxc_cli_integration
pip (or pipx) install .
```