from chameleon.compiler import Compiler as ParentCompiler
from chameleon.compiler import NameTransform
from chameleon.compiler import ExpressionTransform
from chameleon.compiler import COMPILER_INTERNALS_OR_DISALLOWED
from chameleon.compiler import store_econtext
from chameleon.utils import ListDictProxy
from chameleon.astutil import NameLookupRewriteVisitor
from chameleon.astutil import node_annotations
from chameleon.astutil import ast
from chameleon.astutil import store
from chameleon.astutil import load
from chameleon.codegen import TemplateCodeGenerator

class Compiler(ParentCompiler):
    def visit(self, node):
        if node is None:
            return ()
        kind = type(node).__name__
        #print "kind: ", kind
        visitor = getattr(self, "visit_%s" % kind)
        #print "node: ", node
        iterator = visitor(node)
        return list(iterator)
    
    def visit_Assignment(self, node):
        for name in node.names:
            if name in COMPILER_INTERNALS_OR_DISALLOWED:
                raise TranslationError(
                    "Name disallowed by compiler.", name
                    )

            if name.startswith('__'):
                raise TranslationError(
                    "Name disallowed by compiler (double underscore).",
                    name
                    )

        #print node.expression
        assignment = self._engine(node.expression, store("__value"))

        if len(node.names) != 1:
            target = ast.Tuple(
                elts=[store_econtext(name) for name in node.names],
                ctx=ast.Store(),
            )
        else:
            target = store_econtext(node.names[0])

        assignment.append(ast.Assign(targets=[target], value=load("__value")))

        for name in node.names:
            if not node.local:
                assignment += template(
                    "rcontext[KEY] = __value", KEY=ast.Str(s=native_string(name))
                    )

        return assignment
    
    def __init__(self, engine_factory, node, builtins={}, strict=True):
        self._scopes = [set()]
        self._expression_cache = {}
        self._translations = []
        self._builtins = builtins
        self._aliases = [{}]
        self._macros = []
        self._current_slot = []
        
        #print "-------------"
        #print "IN COMPILER"
        #print "-------------"

        internals = COMPILER_INTERNALS_OR_DISALLOWED | \
                    set(self.defaults)

        transform = NameTransform(
            self.global_builtins | set(builtins),
            ListDictProxy(self._aliases),
            internals,
            )

        self._visitor = visitor = NameLookupRewriteVisitor(transform)
        #print vars(self._visitor)

        self._engine = ExpressionTransform(
            engine_factory,
            self._expression_cache,
            visitor,
            strict=strict,
            )

        if isinstance(node_annotations, dict):
            self.lock.acquire()
            backup = node_annotations.copy()
        else:
            backup = None

        try:
            module = ast.Module([])
            module.body += self.visit(node)
            ast.fix_missing_locations(module)
            generator = TemplateCodeGenerator(module)
        finally:
            if backup is not None:
                node_annotations.clear()
                node_annotations.update(backup)
                self.lock.release()

        self.code = generator.code