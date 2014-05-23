from functools import partial
from os.path import dirname

from ..template import MyBaseTemplate, MyBaseTemplateFile
from ..tales import ExPythonExpr
from program import MacroProgram

from chameleon.zpt.template import PageTemplate

from chameleon.tales import PythonExpr
from chameleon.tales import StringExpr
from chameleon.tales import NotExpr
from chameleon.tales import ExistsExpr
from chameleon.tales import ImportExpr
from chameleon.tales import ProxyExpr
from chameleon.tales import StructureExpr
from chameleon.tales import ExpressionParser
from chameleon.loader import TemplateLoader
from chameleon.astutil import Builtin

class MyPageTemplate(PageTemplate, MyBaseTemplate):
    expression_types = {
        'python': ExPythonExpr,
        'string': StringExpr,
        'not': NotExpr,
        'exists': ExistsExpr,
        'import': ImportExpr,
        'structure': StructureExpr,
        }
    
    def parse(self, body):
        if self.literal_false:
            default_marker = ast.Str(s="__default__")
        else:
            default_marker = Builtin("False")

        return MacroProgram(
            body, self.mode, self.filename,
            escape=True if self.mode == "xml" else False,
            default_marker=default_marker,
            boolean_attributes=self.boolean_attributes,
            implicit_i18n_translate=self.implicit_i18n_translate,
            implicit_i18n_attributes=self.implicit_i18n_attributes,
            trim_attribute_space=self.trim_attribute_space,
            )
    
    def __init__(self, body, **config):
        super(MyPageTemplate, self).__init__(body, **config)

class PageTemplateFile(MyPageTemplate, MyBaseTemplateFile):
    expression_types = MyPageTemplate.expression_types.copy()
    expression_types['load'] = partial(
        ProxyExpr, '__loader',
        ignore_prefix=False
    )

    prepend_relative_search_path = True

    def __init__(self, filename, search_path=None, loader_class=TemplateLoader,
                 **config):
        super(PageTemplateFile, self).__init__(filename, **config)

        if search_path is None:
            search_path = []
        else:
            if isinstance(search_path, string_type):
                search_path = [search_path]
            else:
                search_path = list(search_path)

        # If the flag is set (this is the default), prepend the path
        # relative to the template file to the search path
        if self.prepend_relative_search_path:
            path = dirname(self.filename)
            search_path.insert(0, path)

        loader = loader_class(search_path=search_path, **config)
        template_class = type(self)

        # Bind relative template loader instance to the same template
        # class, providing the same keyword arguments.
        self._loader = loader.bind(template_class)

    def _builtins(self):
        d = super(PageTemplateFile, self)._builtins()
        d['__loader'] = self._loader
        return d