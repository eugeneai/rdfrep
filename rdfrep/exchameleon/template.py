import sys

from chameleon.template import BaseTemplate, BaseTemplateFile
from chameleon.template import log
from chameleon.template import _make_module_loader
from chameleon.utils import Scope
from chameleon.utils import join
from chameleon.utils import create_formatted_exception
from chameleon.utils import raise_with_traceback
from chameleon.exc import ExceptionFormatter
from compiler import Compiler

class MyBaseTemplate(BaseTemplate):

    def _compile(self, program, builtins):
        #print "----------------------"
        #print "engine: ", vars(self.engine)
        #print "----------------------"
        #print "strict: ", self.strict
        #print "----------------------"
        #print vars(program.program)
        #print "----------------------"
        compiler = Compiler(self.engine, program, builtins, strict=self.strict)
        #print 1
        return compiler.code
    
    def cook(self, body):
        builtins_dict = self.builtins.copy()
        builtins_dict.update(self.extra_builtins)
        names, builtins = zip(*sorted(builtins_dict.items()))
        digest = self.digest(body, names)
        program = self._cook(body, digest, names)

        initialize = program['initialize']
        functions = initialize(*builtins)

        for name, function in functions.items():
            setattr(self, "_" + name, function)

        self._cooked = True

        if self.keep_body:
            self.body = body
    
    def render(self, **__kw):
        econtext = Scope(__kw)
        rcontext = {}
        self.cook_check()
        stream = self.output_stream_factory()
        try:
            self._render(stream, econtext, rcontext)
        except LookupError:
            cls, exc, tb = sys.exc_info()
            print cls
            print exc
            print tb
	except:
            cls, exc, tb = sys.exc_info()
            print cls
            print exc
            print tb
            errors = rcontext.get('__error__')
            print errors
            if errors:
                formatter = exc.__str__
                if isinstance(formatter, ExceptionFormatter):
                    if errors is not formatter._errors:
                        formatter._errors.extend(errors)
                    raise

                formatter = ExceptionFormatter(errors, econtext, rcontext)

                try:
                    exc = create_formatted_exception(exc, cls, formatter)
                except TypeError:
                    pass

                raise_with_traceback(exc, tb)

            raise

        return join(stream)

class MyBaseTemplateFile(BaseTemplateFile):
    def cook_check(self):
        if self.auto_reload:
            mtime = self.mtime()

            if mtime != self._v_last_read:
                self._v_last_read = mtime
                self._cooked = False

        if self._cooked is False:
            body = self.read()
            log.debug("cooking %r (%d bytes)..." % (self.filename, len(body)))
            self.cook(body)