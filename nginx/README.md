nginx config
============

Defense by numbers: making problems for script kiddies and scanner monkeys
--------------------------------------------------------------------------

This directory contains scripts used as part of my [response|status] code research

This nginx configuration is an example of a nginx reverse proxy (setup to proxy traffic to http://www.google.at) that alters the response codes of returned content.

This nginx.conf script was tested with Debian 7 (nginx-extras pack)


usage:
------

- Install nginx-extras (or compile from source with appropriate modules)
- Copy nginx.conf to /etc/nginx/nginx.conf
- Edit the proxy_pass within nginx.conf to point to the server/webapp you wish to proxy
- Restart nginx
- Profit

note:
-----

Due to a quirk in nginx, although the following codes ARE supported, the reverse proxy returns a response without response|status code (nil)

effected codes:

- 203
- 305
- 306
- 414
- 505
- 506