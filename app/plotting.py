import base64
from io import BytesIO
from typing import Dict, Tuple

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt


def plot_function(f_expr: sp.Expr, vars_syms: Tuple[sp.Symbol, ...], solution: Dict, show_3d: bool = False, grid: float = 5.0, n: int = 100) -> str:
    if len(vars_syms) != 2:
        raise ValueError("Solo se pueden graficar funciones de 2 variables.")
    x, y = vars_syms
    f = sp.lambdify((x, y), f_expr, 'numpy')

    X = np.linspace(-grid, grid, n)
    Y = np.linspace(-grid, grid, n)
    X, Y = np.meshgrid(X, Y)
    Z = f(X, Y)

    fig = plt.figure(figsize=(5, 4))
    if show_3d:
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.7)
        if solution and 'vars' in solution and 'fval' in solution:
            sx = solution['vars'].get(str(x))
            sy = solution['vars'].get(str(y))
            if sx is not None and sy is not None:
                ax.scatter(sx, sy, solution['fval'], c='r', s=50)
        ax.set_xlabel(str(x))
        ax.set_ylabel(str(y))
        ax.set_zlabel('f')
    else:
        CS = plt.contour(X, Y, Z, levels=20)
        plt.clabel(CS, inline=True, fontsize=8)
        if solution and 'vars' in solution:
            sx = solution['vars'].get(str(x))
            sy = solution['vars'].get(str(y))
            if sx is not None and sy is not None:
                plt.scatter(sx, sy, c='r', marker='x', s=100)
        plt.xlabel(str(x))
        plt.ylabel(str(y))

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    return data
