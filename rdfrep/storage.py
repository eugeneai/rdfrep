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
            #g.parse("http://www.w3.org/People/Berners-Lee/card")
            g.parse('example.rdf')
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
    
    def remove(self):
        self.graph.remove((None,None,None))
        self.graph.commit()
    
    def test(self):
        print self.graph.serialize(format='n3')
        #print len(self.graph)
        #Type=rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
        #HTML=rdflib.URIRef('http://www.w3.org/DesignIssues/Overview.html')
        #for s,p,o in self.graph.triples((PERSON, None, None)):
        #    print "-----",(p,o)

    def title(self, name):
	return self.graph.value(HTML,name)

    def value(self, subject=None, predicate=None):
        return self.graph.value(subject,predicate).split(':')[1]

if __name__=="__main__":
    g = RDFStorage()
    #g.remove()
    g.test()
    #print g.title('http://purl.org/dc/elements/1.1/title')
    obj = g.toRDF('http://www.w3.org/People/Berners-Lee/card#p')
    phone = FOAF.phone #g.toRDF('http://xmlns.com/foaf/0.1/phone')
    birthday = g.toRDF('http://xmlns.com/foaf/0.1/birthday')
    office = g.toRDF('http://www.w3.org/2000/10/swap/pim/contact#office')
    ophone = g.toRDF('http://www.w3.org/2000/10/swap/pim/contact#phone')
    print g.value(obj,phone)
    #print RDFs.Class
    #print g.get_class(people.i)
    #print ns.isclass
    g.close_graph()