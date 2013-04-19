# PoC Reverse Proxy MITM-PROXY script to rewrite all response|status codes to values known to delay and/or block browsers and scanning tools
#
# ChrisJohnRiley April 2013

import random

def response(context, flow):
    if debug:
        print ' [ ] Received: ' + str(flow.response.code) + ' ' + flow.response.msg,

    # alter response code and message
    # randomised
    rand = random.choice(response_codes.keys())
    flow.response.code = int(rand)
    flow.response.msg = response_codes[rand]
    if debug:
        print ' [-] Altered: ' + str(flow.response.code) + ' ' + flow.response.msg

response_codes = {
# 100
    '100': 'Continue',
    '101': 'Switching Protocols',
    '102': 'Processing',
# 200
#    '204': 'No Content', # Not implemented in testing, may be useful
# 300
#    '304': 'Not Modified' # Not implemented in testing, may be useful
    }
debug = False
