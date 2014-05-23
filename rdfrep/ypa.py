from pyramid_chameleon import renderer
from pyramid_chameleon import zpt

def renderer_factory(info):
    return renderer.template_renderer_factory(info, MyZPTTemplateRenderer)
  
class MyZPTTemplateRenderer(zpt.ZPTTemplateRenderer):
    def __call__(self, value, system):
        try:
	    system.update(value)
	except (TypeError, ValueError):
	    raise ValueError('renderer was passed non-dictionary as value')
	result = self.template(**system)
	return result