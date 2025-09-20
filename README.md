# keepassxc-cli-integration



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
    - run
      - {{command}} (Run another program with query from KeePassXC)
       

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

The query in `kpx run` has the following format:
`@kpx::{{url}}::{{login or password}}::{{name(optional)}}@kpx`
```shell
kpx run poetry publish --build --username=__token__ --password=@kpx::pypi.org::password::pypi_token@kpx
```


Can be used in scripts:
```powershell
# example.ps1
$VeraCrypt = "C:\Program Files\VeraCrypt\VeraCrypt.exe"
$password = kpx get passoword example-vault

& $VeraCrypt /volume "C:\example\vault.hc" /letter Y /password $password /b /q
```
or
```powershell
# example_2.ps1
$VeraCrypt = "C:\Program Files\VeraCrypt\VeraCrypt.exe"

kpx run $VeraCrypt /volume "C:\example\vault.hc" /letter Y /password @kpx::example-vault::password@kpx /b /q
```


# Installation

1. pip / pipx
```
pip (or pipx) install keepassxc-cli-integration
```
2. git
```
git clone https://github.com/overgodofchaos/keepassxc_cli_integration.git
cd keepassxc-cli-integration
pip (or pipx) install .
```