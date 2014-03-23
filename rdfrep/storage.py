#!/usr/bin/env python
import rdflib
import rdflib.store as store
from rdflib import Namespace
from rdflib.namespace import FOAF, RDF

PERSON_PT = rdflib.Literal('person.pt')
dc = Namespace('http://purl.org/dc/elements/1.1/')
people = Namespace('http://www.w3.org/People/Berners-Lee/card#')
CLASS = rdflib.URIRef('http://www.exaple.com/test/class')
PERSON_CLASS = rdflib.URIRef('http://www.exaple.com/test/class#person')
PT = rdflib.URIRef('http://www.exaple.com/test/pt')
HTML=rdflib.URIRef('http://www.w3.org/DesignIssues/Overview.html')

class RDFStorage():
    def load_graph(self,store="KyotoCabinet",path="/home/paskal/python/rdfstore"):
        ident = rdflib.URIRef("rdflib_test")
        g=rdflib.Graph(store=store, identifier=ident)
        g.open(path, create=True)
        
        if len(g)==0:
            g.parse("http://www.w3.org/People/Berners-Lee/card")
            for p in g.subjects(RDF.type, FOAF.Person):
	        g.add((p, CLASS, PERSON_CLASS))
	    g.add((PERSON_CLASS, PT, PERSON_PT))
            g.commit()
            print "A graph has been obtained and loaded."
            
        print("graph has %s statements." % len(g))
        return g

    def __init__(self,store="KyotoCabinet",path="/home/paskal/python/rdfstore"):
        self.graph=self.load_graph(store,path)
    
    def close_graph(self):
        self.graph.close()
        return True
    
    def toRDF(self, string):
        return rdflib.URIRef(string)
    
    def get_pt(self, obj):
        obj_class = self.graph.value(obj, CLASS)
        return self.graph.value(obj_class, PT)
    
    def test(self):
        #print self.graph.serialize(format='n3')
        self.graph.remove((None,None,None))
        #print len(self.graph)
        #Type=rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
        #HTML=rdflib.URIRef('http://www.w3.org/DesignIssues/Overview.html')
        #for s,p,o in self.graph.triples((PERSON, None, None)):
        #    print "-----",(p,o)

    def title(self, name):
	return self.graph.value(HTML,name)

if __name__=="__main__":
    g = RDFStorage()
    #g.test()
    #g.graph.commit()
    #print g.title('http://purl.org/dc/elements/1.1/title')
    print g.get_pt(people.i)
    #print g.get_class(people.i)
    #print ns.isclass
    g.close_graph()