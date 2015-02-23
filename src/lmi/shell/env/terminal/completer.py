import re
from lmi.shell import obj


def complete_ns(expr_obj, expr, attr):
    '''
    Completes a :py:class:`.LMINamespace`.
    '''
    matches = [
        ns.replace('/', '.')
        for ns in expr_obj.namespaces
        if ns.startswith(attr)
    ]

    return [expr + '.' + match for match in matches]


def complete(completer, user_ns, text):
    m = re.match(r'(\S+(\.\w+)*)\.(\w*)$', text)

    if not m:
        return []

    expr, attr = m.group(1, 3)
    expr_obj = eval(expr, user_ns)

    if isinstance(expr_obj, obj.LMINamespace):
        return complete_ns(expr_obj, expr, attr)

    return []
