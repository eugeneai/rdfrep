from exchameleon.zpt.template import PageTemplateFile

from pyramid.decorator import reify
from pyramid_chameleon import renderer
from pyramid_chameleon import zpt

def renderer_factory(info):
    return renderer.template_renderer_factory(info, MyZPTTemplateRenderer)

class PyramidPageTemplateFile(PageTemplateFile):
    def cook(self, body):
        PageTemplateFile.cook(self, body)
        if self.macro:
            # render only the portion of the template included in a
            # define-macro named the value of self.macro
            macro_renderer = self.macros[self.macro].include
            self._render = macro_renderer

class MyZPTTemplateRenderer(zpt.ZPTTemplateRenderer):
    @reify # avoid looking up reload_templates before manager pushed
    def template(self):
        tf = PyramidPageTemplateFile(
            self.path,
            auto_reload=self.lookup.auto_reload,
            debug=self.lookup.debug,
            translate=self.lookup.translate,
            macro=self.macro,
            )
        return tf

def test():
    path_regex = re.compile(
        r'^(?:(not):\s*)*((?:[A-Za-z_][A-Za-z0-9_:]*)' +
        r'(?:/[?A-Za-z_@\-+][?A-Za-z0-9_@\-\.+/:]*)*)$')
    string = "graph.title(graph.toRDF(dc:title))"
    string = string.strip()
    m = path_regex.match(string)
    nocall, path = m.groups()
    parts = str(path).split('/')
    call = load(str(not nocall))
    base = load(parts[0])
    name = base.id
    ns_used = ':' in name
    if ns_used:
        namespace, name = name.split(':',1)
        #base = namespaces.function_namespaces[namespace](base)
        print namespaces["XML_NS"]
    return string

class Qwer():
    def __init__(self):
        self.name = "name"
    
    def setOpt(self):
        self.prop = "prop"
    
class Rewq(Qwer):
    def setOpt(self):
        
        self.prop = "porp"
        Qwer.setOpt(self)
  
if __name__=="__main__":
    print test()
