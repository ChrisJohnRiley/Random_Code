# PoC Reverse Proxy MITM-PROXY script to rewrite all response|status codes to values known to be accepted and displayed by browsers as html content
#
# ChrisJohnRiley April 2013

import random

def response(context, flow):
    if debug:
        print ' [ ] Received: ' + str(flow.response.code) + ' ' + flow.response.msg,

    if(flow.response.code >= 301 and flow.response.code <= 303):
        # Do not change response codes on 301 - 303
        # Redirects need to be followed and won't work if response code is not 30X
        if debug:
            print ' [!] Response not altered: %s detected' % flow.response.code
    elif(flow.response.code == 304 or  flow.response.code == 204):
        # Do not change response codes on 304 or 204
        # no /unchanged content
        if debug:
            print ' [!] Response not altered: %s detected' % flow.response.code
    elif(flow.response.code == 401):
        # Do not change response codes on 401 auth required
        # need to request auth from browser / user
        if debug:
            print ' [!] Response not altered: %s detected' % flow.response.code
    elif "^location:" in str(flow.response.headers).lower():
        if debug:
            print ' [!] Response not altered: Location header detected'
    elif "javascript" in str(flow.response.headers).lower():
        # Do not change response codes for JavaScript
        # can be done, but limited code support
        if debug:
            print ' [!] Response not altered: JavaScript Content header detected'
    elif "text/css" in str(flow.response.headers).lower():
        # Do not change response codes for CSS
        # can be done, but limited code support
        if debug:
            print ' [!] Response not altered: CSS Content header detected'
    else:
        # randomise response code and appropriate message
        rand = random.choice(response_codes.keys())
        flow.response.code = int(rand)
        flow.response.msg = response_codes[rand]
        if debug:
            print ' [-] Altered: ' + str(flow.response.code) + ' ' + flow.response.msg

# response codes known to work (render html) across all common browsers
# limited to response codes supported by the Apache project
response_codes = {
# 200
    '200': 'OK',
    '201': 'Created',
    '202': 'Accepted',
    '203': 'Non-Authoritative Information',
    '206': 'Partial Content',
    '207': 'Multi-Status',
# 300
    '300': 'Multiple Choices',
    '305': 'Use Proxy',
    '306': 'Switch Proxy',
#400
    '400': 'Bad Request',
    '401': 'Unauthorized',
    '402': 'Payment Required',
    '403': 'Forbidden',
    '404': 'Not Found',
    '405': 'Method Not Allowed',
    '406': 'Not Acceptable',
    '409': 'Conflict',
    '410': 'Gone',
    '411': 'Length Required',
    '412': 'Precondition Failed',
    '413': 'Request Entity Too Large',
    '414': 'Request-URI Too Long',
    '415': 'Unsupported Media Type',
    '416': 'Requested Range Not Satisfiable',
    '417': 'Expectation Failed',
    '418': 'I\'m a teapot',
    '420': 'Enhance Your Calm',
    '422': 'Unprocessable Entity',
    '423': 'Locked',
    '424': 'Failed Dependency',
    '425': 'Unordered Collection',
    '425': 'Method Failure',
    '426': 'Upgrade Required',
# 500
    '500': 'Internal Server Error',
    '501': 'Not Implemented',
    '502': 'Bad Gateway',
    '503': 'Service Unavailable',
    '504': 'Gateway Timeout',
    '505': 'HTTP Version Not Supported',
    '506': 'Variant Also Negotiates',
    '507': 'Insufficient Storage',
    '508': 'Loop Detected',
    '509': 'Bandwidth Limit Exceeded',
    '510': 'Not Extended'
    }
debug = False
