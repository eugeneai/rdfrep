#!/usr/bin/env python
import rdflib
import rdflib.store as store
from rdflib.namespace import RDF
from rdflib.namespace import FOAF

class RDFStorage():
    def load_graph(self,store="KyotoCabinet",path="/home/paskal/python/rdfstore"):
        ident = rdflib.URIRef("rdflib_test")
        g=rdflib.Graph(store=store, identifier=ident)
        g.open(path, create=True)
        
        if len(g)==0:
            g.parse("http://www.w3.org/People/Berners-Lee/card")
            g.commit()
            print "A graph has been obtained and loaded."
            
        print("graph has %s statements." % len(g))
        return g

    def __init__(self,store="KyotoCabinet",path="/home/paskal/python/rdfstore"):
        self.graph=self.load_graph(store,path)
          
    def close_graph(self):
        self.graph.close()
    
    def test(self):
        Type=rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
        HTML=rdflib.URIRef('http://www.w3.org/DesignIssues/Overview.html')
        for s,p,o in self.graph.triples((HTML, None, None)):
            print "-----",(p,o)

    def title(self):
        HTML=rdflib.URIRef('http://www.w3.org/DesignIssues/Overview.html')
        Title=rdflib.URIRef('http://purl.org/dc/elements/1.1/title')
        for obj in self.graph.objects(HTML,Title):
	  return obj

if __name__=="__main__":
    g = RDFStorage()
    print g.title()
    g.close_graph()