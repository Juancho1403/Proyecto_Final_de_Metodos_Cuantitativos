import flet as ft
import sympy as sp
from typing import Dict, Tuple

from .parsing import parse_variables, parse_objective, parse_scipy_constraints, parse_equalities_text
from .optimizers import UnconstrainedSolver, GradientDescentSolver, LagrangeSolver, ConstrainedSciPySolver
from .plotting import plot_function


def OptimizerView(page: ft.Page) -> ft.Control:
    # Inputs
    txt_objective = ft.TextField(
        label="Función objetivo",
        hint_text="Ej: x**2 + y**2",
        helper_text="Escribe la función en notación SymPy (usa ** para potencias)",
        multiline=True,
        min_lines=2,
        expand=True,
    )
    txt_vars = ft.TextField(
        label="Variables",
        hint_text="Ej: x,y",
        helper_text="Lista separada por comas (los nombres deben coincidir con la función)",
    )
    txt_constraints = ft.TextField(
        label="Restricciones",
        hint_text="Una por línea. Ej: x + y - 1 = 0,  x >= 0,  y <= 2",
        helper_text="Usa '=' para igualdad y '>=', '<=' para desigualdades",
        multiline=True,
        min_lines=3,
        expand=True,
    )
    cb_method = ft.Dropdown(
        label="Método",
        options=[
            ft.dropdown.Option("Sin restricciones (minimización directa)"),
            ft.dropdown.Option("Gradiente descendente"),
            ft.dropdown.Option("Método de Lagrange (igualdad)"),
            ft.dropdown.Option("Con restricciones (general)"),
        ],
        value="Sin restricciones (minimización directa)",
        expand=True,
    )

    switch_3d = ft.Switch(label="Mostrar 3D", value=False)

    txt_results = ft.TextField(
        label="Resultados",
        multiline=True,
        read_only=True,
        min_lines=8,
        expand=True,
    )

    plot_img = ft.Image(expand=True, fit=ft.ImageFit.CONTAIN, visible=False)

    # State holder
    last_solution = {"value": None}

    # File picker (to load .txt problems)
    fp = ft.FilePicker()
    page.overlay.append(fp)
    auto_solve_switch = ft.Switch(label="Resolver al cargar", value=True)

    def parse_txt_problem(text: str):
        # Flexible parser:
        # Supports either labeled keys or simple 3-block format
        # Labeled example:
        #   objetivo: x**2 + y**2
        #   variables: x,y
        #   restricciones:
        #     x + y - 1 = 0
        #     x >= 0
        # Simple example:
        #   x**2 + y**2
        #   x,y
        #   x + y - 1 = 0
        #   x >= 0
        lines = [ln.strip() for ln in text.splitlines()]
        # Try labeled first
        obj, vars_line, cons_lines = None, None, []
        mode = None
        for ln in lines:
            if not ln:
                continue
            lower = ln.lower()
            if lower.startswith("objetivo:") or lower.startswith("funcion:") or lower.startswith("función:"):
                obj = ln.split(":", 1)[1].strip()
                mode = "obj"
            elif lower.startswith("variables:"):
                vars_line = ln.split(":", 1)[1].strip()
                mode = "vars"
            elif lower.startswith("restricciones:"):
                mode = "cons"
            else:
                if mode == "cons":
                    cons_lines.append(ln)

        if obj is None or vars_line is None:
            # Fallback simple format: first non-empty line objective, second variables, rest constraints
            non_empty = [ln for ln in lines if ln]
            if len(non_empty) >= 2:
                obj = obj or non_empty[0]
                vars_line = vars_line or non_empty[1]
                cons_lines = non_empty[2:]
            else:
                raise ValueError("Formato de archivo .txt no válido. Se esperan al menos 2 líneas: objetivo y variables.")

        return obj, vars_line, "\n".join(cons_lines)

    def on_file_result(e: ft.FilePickerResultEvent):
        try:
            if not e.files:
                return
            path = e.files[0].path
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            obj, vars_line, cons_text = parse_txt_problem(content)
            txt_objective.value = obj
            txt_vars.value = vars_line
            txt_constraints.value = cons_text
            txt_objective.update(); txt_vars.update(); txt_constraints.update()
            if auto_solve_switch.value:
                on_solve(None)
        except Exception:
            txt_results.value = "❌ Error al cargar el archivo: formato no válido. Revisa los ejemplos del README."
            txt_results.update()

    fp.on_result = on_file_result

    # Helpers
    def _read_inputs():
        objective = txt_objective.value.strip()
        variables_text = txt_vars.value.strip()
        constraints_text = txt_constraints.value.strip()
        if not objective or not variables_text:
            raise ValueError("Debes ingresar la función objetivo y las variables.")
        vars_syms = parse_variables(variables_text)
        f_expr = parse_objective(objective)
        return f_expr, vars_syms, constraints_text

    # Validaciones en vivo
    def validate_objective(e=None):
        try:
            if txt_objective.value.strip():
                parse_objective(txt_objective.value)
            txt_objective.error_text = None
        except Exception:
            txt_objective.error_text = "Expresión inválida. Revisa la notación SymPy (usa **, *, etc.)."
        txt_objective.update()

    def validate_vars(e=None):
        try:
            if txt_vars.value.strip():
                parse_variables(txt_vars.value)
            txt_vars.error_text = None
        except Exception:
            txt_vars.error_text = "Variables inválidas. Usa nombres separados por comas: x,y,z"
        txt_vars.update()

    def validate_constraints(e=None):
        try:
            if txt_constraints.value.strip() and txt_vars.value.strip():
                # Solo valida si también hay variables
                vars_syms = parse_variables(txt_vars.value)
                parse_scipy_constraints(vars_syms, txt_constraints.value)
            txt_constraints.error_text = None
        except Exception:
            txt_constraints.error_text = "Restricciones inválidas. Revisa el formato (ver ayuda)."
        txt_constraints.update()

    txt_objective.on_change = validate_objective
    txt_vars.on_change = lambda e: (validate_vars(), validate_constraints())
    txt_constraints.on_change = validate_constraints

    # Diálogo de ayuda
    help_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Ayuda"),
        content=ft.Column(
            tight=True,
            controls=[
                ft.Text("Formato de entrada:"),
                ft.Text("• Función objetivo: notación SymPy. Ej: x**2 + y**2"),
                ft.Text("• Variables: separadas por comas. Ej: x,y"),
                ft.Text("• Restricciones (una por línea):"),
                ft.Text("   - Igualdad: x + y - 1 = 0"),
                ft.Text("   - Desigualdades: x >= 0,  y <= 2"),
                ft.Text("Puedes cargar un .txt con estos campos (ver README)."),
            ],
        ),
        actions=[ft.TextButton("Cerrar", on_click=lambda e: setattr(page, 'dialog', None) or page.close_dialog())],
    )

    def open_help(e):
        page.dialog = help_dialog
        help_dialog.open = True
        page.update()

    # Event handlers
    def on_solve(e):
        try:
            f_expr, vars_syms, constraints_text = _read_inputs()
            method = cb_method.value

            if "Gradiente" in method:
                solver = GradientDescentSolver()
                res = solver.solve(f_expr, vars_syms, constraints_text)
            elif "Lagrange" in method:
                eqs = parse_equalities_text(constraints_text)
                solver = LagrangeSolver(equalities=eqs)
                res = solver.solve(f_expr, vars_syms, constraints_text)
            elif "Sin restricciones" in method and not constraints_text:
                solver = UnconstrainedSolver()
                res = solver.solve(f_expr, vars_syms, constraints_text)
            else:
                cons = parse_scipy_constraints(vars_syms, constraints_text)
                solver = ConstrainedSciPySolver(scipy_constraints=cons)
                res = solver.solve(f_expr, vars_syms, constraints_text)

            if res.get("vars"):
                out = [f"✔ Método: {method}", ""]
                for k, v in res["vars"].items():
                    out.append(f"{k} = {v:.6f}")
                out.append("")
                out.append(f"Valor óptimo f = {res['fval']:.6f}")
                txt_results.value = "\n".join(out)
                last_solution["value"] = (f_expr, vars_syms, res)
            else:
                txt_results.value = "❌ No se encontró solución."
                last_solution["value"] = None
            txt_results.update()
        except Exception:
            txt_results.value = "❌ Error al resolver: verifica la función, las variables y las restricciones."
            txt_results.update()

    def on_plot(e):
        if not last_solution["value"]:
            txt_results.value += "\n\n⚠️ Primero resuelve un problema."
            txt_results.update()
            return
        f_expr, vars_syms, res = last_solution["value"]
        try:
            data = plot_function(f_expr, vars_syms, res, show_3d=switch_3d.value)
            plot_img.src_base64 = data
            plot_img.visible = True
            plot_img.update()
        except Exception:
            txt_results.value += "\n\n❌ No se pudo graficar. Asegúrate de tener una solución válida y que la función tenga exactamente 2 variables."
            txt_results.update()

    def on_clear(e):
        txt_objective.value = ""
        txt_vars.value = ""
        txt_constraints.value = ""
        txt_results.value = ""
        plot_img.src_base64 = None
        plot_img.visible = False
        last_solution["value"] = None
        txt_results.update()
        plot_img.update()

    def on_compare(e):
        try:
            f_expr, vars_syms, constraints_text = _read_inputs()
            results = []

            has_constraints = bool(constraints_text.strip())
            eqs = parse_equalities_text(constraints_text)

            gd = GradientDescentSolver().solve(f_expr, vars_syms, constraints_text)
            results.append(("Gradiente descendente", gd))

            if not has_constraints:
                uc = UnconstrainedSolver().solve(f_expr, vars_syms)
                results.append(("Sin restricciones (minimización directa)", uc))

            if eqs:
                lg = LagrangeSolver(equalities=eqs).solve(f_expr, vars_syms, constraints_text)
                results.append(("Método de Lagrange (igualdad)", lg))

            if has_constraints:
                cons = parse_scipy_constraints(vars_syms, constraints_text)
                cg = ConstrainedSciPySolver(scipy_constraints=cons).solve(f_expr, vars_syms, constraints_text)
                results.append(("Con restricciones (general)", cg))

            lines = ["📊 Comparación de métodos", ""]
            for name, r in results:
                if r.get("vars"):
                    lines.append(f"• {name}:")
                    var_str = ", ".join([f"{k}={v:.4f}" for k, v in r["vars"].items()])
                    lines.append(f"  {var_str}")
                    lines.append(f"  f={r['fval']:.6f}")
                else:
                    lines.append(f"• {name}: sin solución")
                lines.append("")
            txt_results.value = "\n".join(lines)
            txt_results.update()
        except Exception:
            txt_results.value = "❌ Error al comparar métodos: revisa los datos de entrada."
            txt_results.update()

    btn_solve = ft.FilledButton("Resolver", icon=ft.Icons.PLAY_ARROW, on_click=on_solve)
    btn_plot = ft.OutlinedButton("Graficar", icon=ft.Icons.SHOW_CHART, on_click=on_plot)
    btn_compare = ft.OutlinedButton("Comparar métodos", icon=ft.Icons.TABLE_CHART, on_click=on_compare)
    btn_clear = ft.TextButton("Limpiar", icon=ft.Icons.CLEAR_ALL, on_click=on_clear)
    btn_load = ft.FilledTonalButton("Cargar .txt", icon=ft.Icons.UPLOAD_FILE, on_click=lambda e: fp.pick_files(allow_multiple=False, allowed_extensions=["txt"]))

    inputs_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Text("Entradas", size=18, weight=ft.FontWeight.BOLD),
                        ft.IconButton(ft.Icons.INFO_OUTLINE, tooltip="Ayuda", on_click=open_help),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    txt_objective,
                    txt_vars,
                    txt_constraints,
                    cb_method,
                    ft.Row(controls=[switch_3d, auto_solve_switch], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row(controls=[btn_solve, btn_plot, btn_compare, btn_clear, btn_load], wrap=True, spacing=10),
                ]
            ),
        )
    )

    results_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Resultados", size=18, weight=ft.FontWeight.BOLD),
                    txt_results,
                    ft.Divider(),
                    ft.Text("Gráfica", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=320, content=plot_img),
                ]
            ),
        )
    )

    layout = ft.ResponsiveRow(
        controls=[
            ft.Container(content=inputs_card, col={'xs': 12, 'md': 6}),
            ft.Container(content=results_card, col={'xs': 12, 'md': 6}),
        ]
    )

    return ft.Column(expand=True, controls=[layout])
