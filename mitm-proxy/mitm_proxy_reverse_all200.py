# PoC Reverse Proxy MITM-PROXY script to rewrite all response|status codes to 200 OK
#
# ChrisJohnRiley April 2013

def response(context, flow):
    if debug:
        print ' [ ] Received: ' + str(flow.response.code) + ' ' + flow.response.msg,

    if(flow.response.code >= 301 and flow.response.code <= 303):
        # Do not change response codes on 301 - 303
        # Redirects need to be followed and won't work if response code is 200
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
        if flow.response.code != respcode:
            # Alter response code and message
            flow.response.code = respcode
            flow.response.msg = respmsg
            if debug:
                print ' [-] Altered: ' + str(flow.response.code) + ' ' + flow.response.msg

# Static variables
respcode = 200
respmsg = "OK"
debug = False
