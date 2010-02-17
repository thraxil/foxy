import sgmllib, re
from twisted.web import proxy, http
import sys
from twisted.python import log
log.startLogging(sys.stdout)
from datetime import datetime
import urllib
from restclient import PUT

PROXY_PORT = 8001

class WordParser(sgmllib.SGMLParser):
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.chardata = []
        self.inBody = False
        self.uri = "not set"

    def start_body(self,attrs):
        self.inBody = True

    def end_body(self):
        self.inBody = False

    def handle_data(self,data):
        if self.inBody:
            self.chardata.append(data)

    def index(self):
        text = ''.join(self.chardata)
        print "Indexing: %s: " % self.uri
        document_id = self.uri + "__" + datetime.now().isoformat()
        document_id = urllib.quote(document_id.replace('/','_'))

        PUT("http://fozzy.thraxil.org:8891/application/foxy_test/document/%s" % document_id,
            params=dict(text=text + "\nURL: " + self.uri))


class FozzyProxyClient(proxy.ProxyClient):
    status = '304'
    def handleHeader(self,key,value):
        proxy.ProxyClient.handleHeader(self,key,value)
        if key.lower() == "content-type":
            if value.split(';')[0] == 'text/html':
                print "text/html: %s" % self.father.uri
                self.parser = WordParser()
                self.parser.uri = self.father.uri

    def handleStatus(self,*args):
        proxy.ProxyClient.handleStatus(self,*args)
        self.status = args[1]

    def handleResponsePart(self,data):
        proxy.ProxyClient.handleResponsePart(self,data)
        if hasattr(self, 'parser'): self.parser.feed(data)

    def handleResponseEnd(self):
        proxy.ProxyClient.handleResponseEnd(self)
        if hasattr(self, 'parser'):
            self.parser.close()
            if self.status == '200':
                self.parser.index()
            del(self.parser)

class FozzyProxyClientFactory(proxy.ProxyClientFactory):
    def buildProtocol(self,addr):
        client = proxy.ProxyClientFactory.buildProtocol(self,addr)
        client.__class__ = FozzyProxyClient
        return client

class FozzyProxyRequest(proxy.ProxyRequest):
    protocols = {'http' : FozzyProxyClientFactory}
    def __init__(self, *args):
        proxy.ProxyRequest.__init__(self,*args)

    def process(self):
        proxy.ProxyRequest.process(self)


class FozzyProxy(proxy.Proxy):
    def __init__(self):
        proxy.Proxy.__init__(self)

    def requestFactory(self,*args):
        return FozzyProxyRequest(*args)

class FozzyProxyFactory(http.HTTPFactory):
    def __init__(self):
        http.HTTPFactory.__init__(self)

    def buildProtocol(self, addr):
        protocol = FozzyProxy()
        return protocol

if __name__ == "__main__":
    from twisted.internet import reactor
    prox = FozzyProxyFactory()
    reactor.listenTCP(PROXY_PORT, prox)
    reactor.run()



	  



    



	  

	  

    






	  


          
	  





              

	  
