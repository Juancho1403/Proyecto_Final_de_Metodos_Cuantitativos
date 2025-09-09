import sympy as sp
import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional


class Optimizer:
    def solve(self, f_expr: sp.Expr, vars_syms: Tuple[sp.Symbol, ...], constraints_text: str = "") -> Dict:
        raise NotImplementedError


class UnconstrainedSolver(Optimizer):
    def solve(self, f_expr: sp.Expr, vars_syms: Tuple[sp.Symbol, ...], constraints_text: str = "") -> Dict:
        grads = [sp.diff(f_expr, v) for v in vars_syms]
        sol = sp.solve(grads, vars_syms, dict=True)
        if not sol:
            return {"vars": {}, "fval": None}
        sol = sol[0]
        fval = float(f_expr.subs(sol))
        return {"vars": {str(v): float(sol[v]) for v in vars_syms if v in sol}, "fval": fval}


class GradientDescentSolver(Optimizer):
    def __init__(self, alpha: float = 0.01, max_iter: int = 2000, tol: float = 1e-6, x0: Optional[np.ndarray] = None):
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.x0 = x0

    def solve(self, f_expr: sp.Expr, vars_syms: Tuple[sp.Symbol, ...], constraints_text: str = "") -> Dict:
        grads = [sp.diff(f_expr, v) for v in vars_syms]
        grad_f = sp.lambdify(vars_syms, grads, "numpy")
        f = sp.lambdify(vars_syms, f_expr, "numpy")

        x = self.x0 if self.x0 is not None else np.zeros(len(vars_syms))
        x = np.array(x, dtype=float)

        for _ in range(self.max_iter):
            g = np.array(grad_f(*x), dtype=float)
            x = x - self.alpha * g
            if np.linalg.norm(g) < self.tol:
                break
        return {"vars": {str(v): float(val) for v, val in zip(vars_syms, x)}, "fval": float(f(*x))}


class LagrangeSolver(Optimizer):
    def __init__(self, equalities: Optional[List[sp.Expr]] = None):
        self.equalities = equalities or []

    def solve(self, f_expr: sp.Expr, vars_syms: Tuple[sp.Symbol, ...], constraints_text: str = "") -> Dict:
        cons_eq = list(self.equalities)
        lambdas = sp.symbols(f"l0:{len(cons_eq)}") if cons_eq else []
        L = f_expr + sum(lambdas[i] * cons_eq[i] for i in range(len(cons_eq)))

        grads = [sp.diff(L, v) for v in list(vars_syms) + list(lambdas)]
        sol = sp.solve(grads, list(vars_syms) + list(lambdas), dict=True)
        if not sol:
            return {"vars": {}, "fval": None}
        sol = sol[0]
        fval = float(f_expr.subs(sol))
        return {"vars": {str(v): float(sol[v]) for v in vars_syms}, "fval": fval}


class ConstrainedSciPySolver(Optimizer):
    def __init__(self, scipy_constraints: Optional[List[Dict]] = None, x0: Optional[np.ndarray] = None):
        self.scipy_constraints = scipy_constraints or []
        self.x0 = x0

    def solve(self, f_expr: sp.Expr, vars_syms: Tuple[sp.Symbol, ...], constraints_text: str = "") -> Dict:
        f = sp.lambdify(vars_syms, f_expr, "numpy")
        x0 = self.x0 if self.x0 is not None else np.ones(len(vars_syms))
        res = minimize(lambda x: f(*x), x0, constraints=self.scipy_constraints)
        return {"vars": {str(v): float(val) for v, val in zip(vars_syms, res.x)}, "fval": float(res.fun)}
