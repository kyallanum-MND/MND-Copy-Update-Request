[![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)](https://www.whitesourcesoftware.com/)  
[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)

# [Mend Copy Update Request Tool](https://github.com/kyallanum-MND/MND-Copy-Update-Request)
This tool allows you to copy update requests
* Allows copying at the project, product, or organization level.
* Allows you to keep the update requests in your filesystem or clean them up.
* Creates a directory structure that mimics the structure in the whitesource UI.

## Supported Operating Systems
- **Windows (PowerShell):** 10

## Prerequisites
* Python 3.6+

## Installation and Execution by cloning this repo:
1. Clone the repo:
```shell
git clone https://github.com/kyallanum-MND/MND-Copy-Update-Request.git
```

2. Run setup.py
```shell
cd MND-Copy-Update-Request
python setup.py install
```

## Full Usage:
```shell
usage: __main__.py [-h] [-t {proj,prod,org}] -se S_ENV -sk S_TOKEN -su S_USER_KEY [-de D_ENV] -dk D_TOKEN [-du D_USER_KEY] -o OUTPUT_DIR [--no-cleanup]

Mend Copy Update Request Tool

optional arguments:
  -h, --help            show this help message and exit
  -t {proj,prod,org}, --type {proj,prod,org}
                        Type of copy (proj, prod, org)
  -se S_ENV, --s-env S_ENV
                        Source Environment
  -sk S_TOKEN, --s-token S_TOKEN
                        Token of object to copy
  -su S_USER_KEY, --s-userkey S_USER_KEY
                        Source UserKey
  -de D_ENV, --d-env D_ENV
                        The destination environment. If none, same as source environment
  -dk D_TOKEN, --d-token D_TOKEN
                        The destination Organization Token.
  -du D_USER_KEY, --d-userkey D_USER_KEY
                        The destination userkey. If none, same as source user key
  -o OUTPUT_DIR, --output OUTPUT_DIR
                        The output directory
  --no-cleanup          Do not cleanup the files created for further inspection
```

## PLEASE NOTE:
- The "-dk" flag will ALWAYS be the destination organization token. The tool will automatically preserve the Product and Project name unless the Product name is not specified, in which case it will insert it into the Product: "Py_Script"

## Examples:
```shell
# Copy Project Update Request for project from saas to app 
mnd_copy_update_request -t proj -se https://saas.whitesourcesoftware.com -sk <Source Project Token> -su <Source User Key> -de https://app.whitesourcesoftware.com -dk <Destination Organization Token> -du <Destination User Key> -o update-requests 

#Copy Product Update Requests from On-Prem Solution to saas
mnd_copy_update_request -t prod -se https://my_on_prem.my_company.com -sk <Source Product Token> -su <Source User Key> -de https://saas.whitesource.com -dk <Destination Organization Token> -du <Destination User Key> -o update-requests

#Copy everything from one organization to another in the same environment
mnd_copy_update_request -t org -se https://saas.whitesourcesoftware.com -sk <Source Organization Token> -su <Source User Key> -dk <Destination Organization Token> -o update-requests
```
