from pyramid.view import view_config
from storage import RDFStorage
from pyramid.renderers import render_to_response

PERSON_PT='templates/person.pt'

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'rdfrep'}

@view_config(route_name='person', renderer=PERSON_PT)
def my_view(request):
    g = RDFStorage()
    return render_to_response(PERSON_PT,
                              {'graph':g,},
                              request=request)