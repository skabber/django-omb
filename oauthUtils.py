from openid.yadis import discover
from omb import OMB_VERSION_01, OMB_UPDATE_PROFILE, OMB_POST_NOTICE, OAUTH_REQUEST, OAUTH_ACCESS, OAUTH_AUTHORIZE, OAUTH_DISCOVERY
from pydataportability.xrds.parser import XRDSParser
import StringIO

def xrdsContainsServices(xrds, service_names):
    for service in service_names:
        if not service in xrds:
            return False
    return True

def getServices(profile_url):
    """
    Returns a dictionary of services provided by the XRDS file that is discovered at the URL that was passed in.
    """
    dis = discover.discover(profile_url)
    # identi.ca doesn't implement XRDS correctly http://xrds-simple.net/core/1.0/
    # This is a hack until laconi.ca fixes http://laconi.ca/trac/ticket/696
    # Either that or the pydataportability needs to accept both $xrd* and $XRD*
    response = StringIO.StringIO(dis.response_text.replace("$xrd*", "$XRD*"))
    
    xrds_services = {}
    
    if dis.isXRDS():
        xrds = XRDSParser(response)
        for service in xrds.services:
            xrds_services[service.type] = service
            if len(xrds_services) < 1:
                # TODO Error XRDS contained no services
                return {}
        if not xrdsContainsServices(xrds_services, [OAUTH_REQUEST, OAUTH_AUTHORIZE, OAUTH_ACCESS]):
            # TODO Error Not all the OAuth services were present in the XRDS
            return {}
        if not xrdsContainsServices(xrds_services, [OMB_POST_NOTICE, OMB_UPDATE_PROFILE]):
            # TDOD Error Not all the OMB services were present in the XRDS
            return {}
        return xrds_services
    else:
        # TODO Not and XRDS
        return {}
