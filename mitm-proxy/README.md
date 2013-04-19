Readme

This directory contains scripts used as part of my [response|status] code research

These scripts are designed to work with mitm-proxy and provide a reverse proxy interface to test browsers and tools. Specifically these scripts were used to test automated scanners to see how they respond to specific response codes and randomised response codes during scans.

Example usage:

=./mitmproxy -s mitm_proxy_reverse_allrnd.py -P http://192.168.0.177:80 -p 80

Further information about the research and the results can be found on blog.c22.cc and are discussed in my BSidesLondon 2013 presentation "Defense by numbers: making problems for script kiddies and scanner monkies"