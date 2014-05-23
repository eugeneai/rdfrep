from pyramid.view import view_config
from storage import RDFStorage, people
from pyramid.renderers import render_to_response, get_renderer
from rdflib.namespace import FOAF, RDF

PERSON_PT='templates/person.pt'
BASE_PT='templates/base.pt'

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'rdfrep'}

@view_config(route_name='person')
def pers_view(request):
    #base = get_renderer(BASE_PT).implementation()
    g = RDFStorage()
    obj = g.toRDF('http://www.w3.org/People/Berners-Lee/card#p')
    return render_to_response(BASE_PT,
                              {'graph':g,
			       'person':obj,
			       'FOAF':FOAF},
                              request=request)