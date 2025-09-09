import sympy as sp
from typing import List, Tuple


def parse_variables(variables_text: str) -> Tuple[sp.Symbol, ...]:
    variables = [v.strip() for v in variables_text.split(',') if v.strip()]
    if not variables:
        raise ValueError("Debe ingresar al menos una variable, ej: x,y")
    return sp.symbols(variables)


def parse_objective(objective_text: str) -> sp.Expr:
    if not objective_text.strip():
        raise ValueError("Debe ingresar la función objetivo")
    return sp.sympify(objective_text)


def parse_equalities_text(constraints_text: str) -> List[sp.Expr]:
    eqs: List[sp.Expr] = []
    for line in constraints_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if '=' in s and ('>=' not in s) and ('<=' not in s):
            left, right = s.split('=')
            eqs.append(sp.sympify(left) - sp.sympify(right))
    return eqs


def parse_scipy_constraints(vars_syms: Tuple[sp.Symbol, ...], constraints_text: str):
    cons = []
    for line in constraints_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if '>=' in s:
            left, right = s.split('>=')
            cons.append({
                'type': 'ineq',
                'fun': sp.lambdify(vars_syms, sp.sympify(left) - sp.sympify(right), 'numpy')
            })
        elif '<=' in s:
            left, right = s.split('<=')
            cons.append({
                'type': 'ineq',
                'fun': sp.lambdify(vars_syms, sp.sympify(right) - sp.sympify(left), 'numpy')
            })
        elif '=' in s:
            left, right = s.split('=')
            cons.append({
                'type': 'eq',
                'fun': sp.lambdify(vars_syms, sp.sympify(left) - sp.sympify(right), 'numpy')
            })
    return cons
