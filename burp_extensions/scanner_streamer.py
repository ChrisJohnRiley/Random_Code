# 14.12.2012 Version 1.0
# alpha quality

from burp import IBurpExtender
from burp import IScannerListener
from burp import IExtensionStateListener
from java.io import PrintWriter

def initExtension():

    #
    # Scanner_Streamer.py
    #
    # This Burp extension will display findings from the burp scanner module as
    # they are discovered. Settings can be made in the script itself to configure
    # verbose mode, duplicate finding notifications, and specify if only in-scope
    # items are displayed.
    #

    # Extension configuration
    #
    # default: {onlyInScope: true, verbose: false, newIssuesOnly: true}
    #

    # show only inscope items (global vars)
    global onlyInScope
    onlyInScope = True
    # verbose output (debugging)
    global verbose
    verbose = False
    # only display NEW issues (avoids duplicate findings from filler output)
    global newIssuesOnly
    newIssuesOnly = True
    global recordedIssues
    recordedIssues = []

    # because ASCII art is oldskool cool
    logo = '''
    MP""""""`MM                                                       
    M  mmmmm..M                                                       
    M.      `YM .d8888b. .d8888b. 88d888b. 88d888b. .d8888b. 88d888b. 
    MMMMMMM.  M 88'  `"" 88'  `88 88'  `88 88'  `88 88ooood8 88'  `88 
    M. .MMM'  M 88.  ... 88.  .88 88    88 88    88 88.  ... 88       
    Mb.     .dM `88888P' `88888P8 dP    dP dP    dP `88888P' dP       
    MMMMMMMMMMM                                                       
    
    MP""""""`MM   dP                                                           
    M  mmmmm..M   88                                                           
    M.      `YM d8888P 88d888b. .d8888b. .d8888b. 88d8b.d8b. .d8888b. 88d888b. 
    MMMMMMM.  M   88   88'  `88 88ooood8 88'  `88 88'`88'`88 88ooood8 88'  `88 
    M. .MMM'  M   88   88       88.  ... 88.  .88 88  88  88 88.  ... 88       
    Mb.     .dM   dP   dP       `88888P' `88888P8 dP  dP  dP `88888P' dP       
    MMMMMMMMMMM
    
                                                // Chris John Riley (c) 2012
                                                          // [ blog.c22.cc ]
    
    ::: config :::
    [ ] Verbose: %s
    [ ] In Scope Only: %s
    [ ] Display only new issues: %s
    
        --------------------------------------------------------------------
    ''' % (str(verbose), str(onlyInScope), str(newIssuesOnly))
    print logo

def domainInScope(self, issue):

    # check domain is in scope - output in verbose mode

    if self._callbacks.isInScope(issue.getUrl()) and onlyInScope:
        if verbose:
            self._stdout.println("[+] Domain (%s) in scope" % issue.getUrl().getHost())
        return True
    elif verbose:
        self._stdout.println("[-] Domain (%s) not in scope" % issue.getUrl().getHost())

def newFinding(issue):

    # create search_string from finding name and hostname
    # continue if not already displayed or if newIssuesOnly is False

    if not newIssuesOnly:
        # return True always
        return True
    else:
        # combine string and check if it exists in the array recordedIssues
        search_string = issue.getIssueName() + ":" + issue.getUrl().getHost()
        if not search_string in recordedIssues:
            # add search string to recordedIssues to skip next time
            recordedIssues.append(search_string)
            return True

def outputFinding(self, issue):

    # output scanner finding

    self._stdout.println("[+] New issue: " + issue.getIssueName())
    self._stdout.println("   [-] Target: " + str(issue.getUrl()))
    self._stdout.println("   [-] Severity: " + str(issue.getSeverity()) + \
        " (" + str(issue.getConfidence()) + ")")
    # returns only int, no actual issue type - removed for now!
    #self._stdout.println("   [-] Issue type: " + str(issue.getIssueType()))

class BurpExtender(IBurpExtender, IScannerListener, IExtensionStateListener):

    # init module settings and variables
    # hoping to make this a GUI option (not sure how yet)


    
    #
    # implement IBurpExtender
    #


    def registerExtenderCallbacks(self, callbacks):
        
        # keep a reference to our callbacks object
        self._callbacks = callbacks
        
        # set our extension name
        callbacks.setExtensionName("Scanner Streamer [c22]")
        
        # obtain our output stream
        self._stdout = PrintWriter(callbacks.getStdout(), True)

        # register ourselves as a Scanner listener
        callbacks.registerScannerListener(self)
        
        # register ourselves as an extension state listener
        callbacks.registerExtensionStateListener(self)
        
        # call initExtension routine
        initExtension()

        return


    #
    # implement IScannerListener
    #

    def newScanIssue(self, issue):
        
        if domainInScope(self, issue):
            # check if finding already displayed for this hostname
            if newFinding(issue):
                outputFinding(self, issue)
            else:
                # already displayed
                if verbose:
                    self._stdout.println("[-] Finding already displayed (%s)" % issue.getIssueName())

        return

    #
    # implement IExtensionStateListener
    #

    def extensionUnloaded(self):

        self._stdout.println("\n[!] Scanner_Streamer.py extension was unloaded")
        return
