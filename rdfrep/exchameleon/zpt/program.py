from functools import partial

from chameleon.zpt.program import MacroProgram as ParentMacroProgram
from chameleon.zpt.program import validate_attributes
from chameleon.zpt.program import skip
from chameleon.zpt.program import wrap
from chameleon.zpt.program import EMPTY_DICT

from chameleon import nodes
from chameleon import tal
from chameleon import metal
from chameleon import i18n

from chameleon.namespaces import XML_NS
from chameleon.namespaces import XMLNS_NS
from chameleon.namespaces import I18N_NS as I18N
from chameleon.namespaces import TAL_NS as TAL
from chameleon.namespaces import METAL_NS as METAL
from chameleon.namespaces import META_NS as META

from chameleon.utils import decode_htmlentities

import time

class MacroProgram(ParentMacroProgram):
    def visit_element(self, start, end, children):
        ns = start['ns_attrs']
        
        ADDITIONAL_ATTRS = {}

        for (prefix, attr), encoded in tuple(ns.items()):
            if prefix == TAL:
                ns[prefix, attr] = decode_htmlentities(encoded)
        
        # Validate namespace attributes
        validate_attributes(ns, TAL, tal.WHITELIST)
        validate_attributes(ns, METAL, metal.WHITELIST)
        validate_attributes(ns, I18N, i18n.WHITELIST)

        # Check attributes for language errors
        self._check_attributes(start['namespace'], ns)

        # Remember whitespace for item repetition
        if self._last is not None:
            self._whitespace = "\n" + " " * len(self._last.rsplit('\n', 1)[-1])

        # Set element-local whitespace
        whitespace = self._whitespace
        
        # Set up switch
        try:
            clause = ns[TAL, 'switch']
        except KeyError:
            switch = None
        else:
            value = nodes.Value(clause)
            switch = value, nodes.Copy(value)

        self._switches.append(switch)

        body = []

        # Include macro
        use_macro = ns.get((METAL, 'use-macro'))
        extend_macro = ns.get((METAL, 'extend-macro'))
        if use_macro or extend_macro:
            omit = True
            slots = []
            self._use_macro.append(slots)

            if use_macro:
                inner = nodes.UseExternalMacro(
                    nodes.Value(use_macro), slots, False
                    )
            else:
                inner = nodes.UseExternalMacro(
                    nodes.Value(extend_macro), slots, True
                    )
        # -or- include tag
        else:
            content = nodes.Sequence(body)

            # tal:content
            try:
                clause = ns[TAL, 'content']
            except KeyError:
                pass
            else:
                clause = self.get_semantic(clause, ns, 'content')

                key, value = tal.parse_substitution(clause)
                xlate = True if ns.get((I18N, 'translate')) == '' else False
                content = self._make_content_node(value, content, key, xlate)

                if end is None:
                    # Make sure start-tag has opening suffix.
                    start['suffix'] = ">"

                    # Explicitly set end-tag.
                    end = {
                        'prefix': '</',
                        'name': start['name'],
                        'space': '',
                        'suffix': '>'
                        }

            # i18n:translate
            try:
                clause = ns[I18N, 'translate']
            except KeyError:
                pass
            else:
                dynamic = ns.get((TAL, 'content')) or ns.get((TAL, 'replace'))

                if not dynamic:
                    content = nodes.Translate(clause, content)

            # tal:attributes
            try:
                clause = ns[TAL, 'attributes']
            except KeyError:
                TAL_ATTRIBUTES = []
            else:
                TAL_ATTRIBUTES = tal.parse_attributes(clause)

            # i18n:attributes
            try:
                clause = ns[I18N, 'attributes']
            except KeyError:
                I18N_ATTRIBUTES = {}
            else:
                I18N_ATTRIBUTES = i18n.parse_attributes(clause)
            
            # Prepare attributes from TAL language
            prepared = tal.prepare_attributes(
                start['attrs'], TAL_ATTRIBUTES,
                I18N_ATTRIBUTES, ns, self.DROP_NS
                )

            # Create attribute nodes
            STATIC_ATTRIBUTES = self._create_static_attributes(prepared)
            ATTRIBUTES = self._create_attributes_nodes(
                prepared, I18N_ATTRIBUTES, STATIC_ATTRIBUTES
                )

            # Start- and end nodes
            start_tag = nodes.Start(
                start['name'],
                self._maybe_trim(start['prefix']),
                self._maybe_trim(start['suffix']),
                ATTRIBUTES
                )

            end_tag = nodes.End(
                end['name'],
                end['space'],
                self._maybe_trim(end['prefix']),
                self._maybe_trim(end['suffix']),
                ) if end is not None else None

            # tal:omit-tag
            try:
                clause = ns[TAL, 'omit-tag']
            except KeyError:
                omit = False
            else:
                clause = clause.strip()

                if clause == "":
                    omit = True
                else:
                    expression = nodes.Negate(nodes.Value(clause))
                    omit = expression

                    # Wrap start- and end-tags in condition
                    start_tag = nodes.Condition(expression, start_tag)

                    if end_tag is not None:
                        end_tag = nodes.Condition(expression, end_tag)

            if omit is True or start['namespace'] in self.DROP_NS:
                inner = content
            else:
                inner = nodes.Element(
                    start_tag,
                    end_tag,
                    content,
                    )

                # Assign static attributes dictionary to "attrs" value
                inner = nodes.Define(
                    [nodes.Alias(["attrs"], STATIC_ATTRIBUTES or EMPTY_DICT)],
                    inner,
                    )

                if omit is not False:
                    inner = nodes.Cache([omit], inner)

            # tal:replace
            try:
                clause = ns[TAL, 'replace']
            except KeyError:
                pass
            else:
                clause = self.get_semantic(clause, ns, 'replace')

                key, value = tal.parse_substitution(clause)
                xlate = True if ns.get((I18N, 'translate')) == '' else False
                inner = self._make_content_node(value, inner, key, xlate)

        # metal:define-slot
        try:
            clause = ns[METAL, 'define-slot']
        except KeyError:
            DEFINE_SLOT = skip
        else:
            DEFINE_SLOT = partial(nodes.DefineSlot, clause)

        # tal:define
        try:
            clause = ns[TAL, 'define']
        except KeyError:
            DEFINE = skip
        else:
            defines = tal.parse_defines(clause)
            if defines is None:
                raise ParseError("Invalid define syntax.", clause)

            DEFINE = partial(
                nodes.Define,
                [nodes.Assignment(
                    names, nodes.Value(expr), context == "local")
                 for (context, names, expr) in defines],
                )

        # tal:case
        try:
            clause = ns[TAL, 'case']
        except KeyError:
            CASE = skip
        else:
            value = nodes.Value(clause)
            for switch in reversed(self._switches):
                if switch is not None:
                    break
            else:
                raise LanguageError(
                    "Must define switch on a parent element.", clause
                    )

            CASE = lambda node: nodes.Define(
                [nodes.Alias(["default"], switch[1], False)],
                nodes.Condition(
                    nodes.Equality(switch[0], value),
                    nodes.Cancel([switch[0]], node),
                ))

        # tal:repeat
        try:
            clause = ns[TAL, 'repeat']
        except KeyError:
            REPEAT = skip
        else:
            defines = tal.parse_defines(clause)
            assert len(defines) == 1
            context, names, expr = defines[0]

            expression = nodes.Value(expr)

            if start['namespace'] == TAL:
                self._last = None
                self._whitespace = whitespace.lstrip('\n')
                whitespace = ""

            REPEAT = partial(
                nodes.Repeat,
                names,
                expression,
                context == "local",
                whitespace
                )

        # tal:condition
        try:
            clause = ns[TAL, 'condition']
        except KeyError:
            CONDITION = skip
        else:
            expression = nodes.Value(clause)
            CONDITION = partial(nodes.Condition, expression)

        # tal:switch
        if switch is None:
            SWITCH = skip
        else:
            SWITCH = partial(nodes.Cache, list(switch))

        # i18n:domain
        try:
            clause = ns[I18N, 'domain']
        except KeyError:
            DOMAIN = skip
        else:
            DOMAIN = partial(nodes.Domain, clause)

        # i18n:name
        try:
            clause = ns[I18N, 'name']
        except KeyError:
            NAME = skip
        else:
            if not clause.strip():
                NAME = skip
            else:
                NAME = partial(nodes.Name, clause)

        # The "slot" node next is the first node level that can serve
        # as a macro slot
        slot = wrap(
            inner,
            DEFINE_SLOT,
            DEFINE,
            CASE,
            CONDITION,
            REPEAT,
            SWITCH,
            DOMAIN,
            )

        # metal:fill-slot
        try:
            clause = ns[METAL, 'fill-slot']
        except KeyError:
            pass
        else:
            if not clause.strip():
                raise LanguageError(
                    "Must provide a non-trivial string for metal:fill-slot.",
                    clause
                )

            index = -(1 + int(bool(use_macro or extend_macro)))

            try:
                slots = self._use_macro[index]
            except IndexError:
                raise LanguageError(
                    "Cannot use metal:fill-slot without metal:use-macro.",
                    clause
                    )

            slots = self._use_macro[index]
            slots.append(nodes.FillSlot(clause, slot))

        # metal:define-macro
        try:
            clause = ns[METAL, 'define-macro']
        except KeyError:
            pass
        else:
            self._macros[clause] = slot
            slot = nodes.UseInternalMacro(clause)

        slot = wrap(
            slot,
            NAME
            )

        # tal:on-error
        try:
            clause = ns[TAL, 'on-error']
        except KeyError:
            ON_ERROR = skip
        else:
            key, value = tal.parse_substitution(clause)
            translate = True if ns.get((I18N, 'translate')) == '' else False

            fallback = self._make_content_node(value, None, key, translate)

            if omit is False and start['namespace'] not in self.DROP_NS:
                start_tag = copy(start_tag)

                start_tag.attributes = nodes.Sequence(
                    start_tag.attributes.extract(
                        lambda attribute:
                        isinstance(attribute, nodes.Attribute) and
                        isinstance(attribute.expression, ast.Str)
                    )
                )

                if end_tag is None:
                    # Make sure start-tag has opening suffix. We don't
                    # allow self-closing element here.
                    start_tag.suffix = ">"

                    # Explicitly set end-tag.
                    end_tag = nodes.End(start_tag.name, '', '</', '>',)

                fallback = nodes.Element(
                    start_tag,
                    end_tag,
                    fallback,
                )

            ON_ERROR = partial(nodes.OnError, fallback, 'error')

        clause = ns.get((META, 'interpolation'))
        if clause in ('false', 'off'):
            INTERPOLATION = False
        elif clause in ('true', 'on'):
            INTERPOLATION = True
        elif clause is None:
            INTERPOLATION = self._interpolation[-1]
        else:
            raise LanguageError("Bad interpolation setting.", clause)

        self._interpolation.append(INTERPOLATION)

        # Visit content body
        for child in children:
            body.append(self.visit(*child))

        self._switches.pop()
        self._interpolation.pop()

        if use_macro:
            self._use_macro.pop()

        return wrap(
            slot,
            ON_ERROR
            )

    def get_semantic(self, clause, ns, statement):
        if 'rdf:' not in clause:
	    return clause
	start, end = clause.split('rdf:')
	subject, predicate = end.strip().split(' ',1)
	clause = start+'graph.graph.value('+subject+','+predicate+')'
        attrClause = 'property '+predicate
        ns[TAL, statement] = clause
        ns[TAL, 'attributes'] = attrClause
        return clause