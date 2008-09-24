from openid.yadis import discover
from omb import OMB_VERSION_01, OMB_UPDATE_PROFILE, OMB_POST_NOTICE, OAUTH_REQUEST, OAUTH_ACCESS, OAUTH_AUTHORIZE, OAUTH_DISCOVERY
from omb.utils.parser import XRDSParser

def getServices(user, profile_url):
    dis = discover.discover(profile_url)
    if dis.isXRDS():
        xrds = XRDSParser(dis.response_text)
        oauth_services = [s for s in xrds.services if s.type == OAUTH_DISCOVERY]
        if len(oauth_services) < 1:
            # TODO Error
            return {}
        oauth_service = oauth_services[0]
        oauth_xrd = [n for n in xrds.xrd if n.id == oauth_service.uris[0].uri[1:]][0]
        
        omb = {}
        oauth_services = [s for s in oauth_xrd.services]
        for service in [OAUTH_REQUEST, OAUTH_AUTHORIZE, OAUTH_ACCESS]:
            for oas in oauth_services:
                if oas.type.find(service) > -1:
                    omb[service] = oas
        if len(omb) != len([OAUTH_REQUEST, OAUTH_AUTHORIZE, OAUTH_ACCESS]):
            # TODO Error
            return {}
        
        omb_services = [s for s in xrds.services if s.type == OMB_VERSION_01] # TODO make that a variable
        if len(omb_services) < 1:
            # TODO Error
            return {}
        omb_service = omb_services[0]
        omb_xrd = [n for n in xrds.xrd if n.id == omb_service.uris[0].uri[1:]][0]
        omb_services = [s for s in omb_xrd.services]
        for s in [OMB_UPDATE_PROFILE, OMB_POST_NOTICE]:
            for ombs in omb_services:
                if ombs.type.find(s) > -1:
                    omb[s] = ombs
        # TODO need validation that all services got added the omb and Error if not
        if not omb[OAUTH_REQUEST].localid.text:
            # TODO Error
            return {}
        return omb