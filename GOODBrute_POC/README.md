GOODBrute POC Example (DeepSec Demo)
====================================

requires:

- Python
- ADB


Simple Python script that wraps ADB commands in order to perform a brute-force
attack on effected GOOD for Enterprise Containers. This script will only function
on  GOOD for Enterprise versions that allow the use of ADB backup (aka those with
the allowBackup:true flag set). Current releases of GOOD have resolved this issue.

Note:

This script is a PoC ONLY and as suh all variables and parameters are hard-coded
This is not meant to be used to attack GOOD for Enterprise containers and is only
released as a PoC example of what is possible.


Reference: CVE-2013-6779