# stolen from pydataportability

from elementtree.ElementTree import parse, fromstring

class URI(object):
    """an URI representation with priority"""

    def __init__(self, uri, method, prio):
        self.uri = uri
        self.prio = prio
        self.method = method
        


class Service(object):
    """a service definition"""
    def __init__(self, typ, uris=[], priority=0, localid=""):
        self.uris = uris
        self.priority = priority
        self.type = typ
        self.localid = localid

class XRD(object):
    """a XRD definition"""
    def __init__(self, xrds, id, servs):
        self.xrds = xrds
        self.id = id
        self.services = servs
        

class XRDSParser(object):
    """parse an xrds document"""
    
    def __init__(self,st):
        #tree = parse(fp)
        #elem = tree.getroot()
        elem = fromstring(st)
        services = elem.findall("*/{xri://$xrd*($v*2.0)}Service")
        self._services = self.createServices(services)
        
        xrd = elem.findall("{xri://$xrd*($v*2.0)}XRD")
        self._xrd = []
        
        for xr in xrd:
            servs = xr.findall("{xri://$xrd*($v*2.0)}Service")
            if xr.attrib.has_key('{http://www.w3.org/XML/1998/namespace}id'):
                x = XRD(xr, xr.attrib['{http://www.w3.org/XML/1998/namespace}id'], self.createServices(servs))
            else:
                x = XRD(xr, None, self.createServices(servs))
            self._xrd.append(x)

    def createServices(self, services):
        servs = []
        for service in services:
            typ = service.find("{xri://$xrd*($v*2.0)}Type").text
            uris = service.findall("{xri://$xrd*($v*2.0)}URI")
            localid = service.find("{xri://$xrd*($v*2.0)}LocalID")
            prio = service.attrib.get('priority',0)
            uri_objects = []
            for uri in uris:
                method = uri.attrib.get("{http://xrds-simple.net/core/1.0}httpMethod","GET")
                prio = uri.attrib.get("{http://xrds-simple.net/core/1.0}priority","0")
                u = URI(uri.text,method,prio)
                uri_objects.append(u)
            s = Service(typ, uri_objects, prio, localid)
            servs.append(s)
        return servs

    @property
    def services(self):
        """return the services found"""
        return self._services
    
    @property
    def xrd(self):
        """return the xrd's found"""
        return self._xrd
        

if __name__=="__main__":        
    fp = open("xrds.xml","r")
    p = XRDSParser(fp)
    fp.close()
    for s in p.services:
        print "Type:",s.type
        print "Prio:",s.priority
        print "LocalID:",s.localid        
        for uri in s.uris:
            print "  ",uri.uri
            
        print 
