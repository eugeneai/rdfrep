import sys

from chameleon.tales import PythonExpr
from chameleon.tales import re_continuation
from chameleon.parser import substitute
from chameleon.utils import ast
from chameleon.exc import ExpressionError

class ExPythonExpr(PythonExpr):
    def translate(self, expression, target):
        # Strip spaces
        string = expression.strip()
        
        #print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        #print string

        # Conver line continuations to newlines
        string = substitute(re_continuation, '\n', string)

        # Convert newlines to spaces
        string = string.replace('\n', ' ')
        try:
            value = self.parse(string)
        except SyntaxError:
            exc = sys.exc_info()[1]
            raise ExpressionError(exc.msg, string)

        # Transform attribute lookups to allow fallback to item lookup
        self.transform.visit(value)

        return [ast.Assign(targets=[target], value=value)]