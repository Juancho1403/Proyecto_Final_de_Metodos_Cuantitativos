# Calculadora de Optimización No Lineal
 
 Aplicación de escritorio construida en Python y Flet que resuelve problemas de optimización no lineal con y sin restricciones. Implementa varios métodos (simbólicos y numéricos), permite comparar resultados y ofrece visualización 2D/3D. Diseñada para el Parcial VI de Métodos Cuantitativos, con enfoque en POO y demostración en vivo.
 
 ## Características principales
 
 - Ingreso de funciones objetivo en notación Python/SymPy, p. ej.: `x**2 + y**2`.
 - Variables múltiples: `x,y,z` (la gráfica aplica para 2 variables).
 - Restricciones de igualdad (`=`) y desigualdad (`>=`, `<=`).
 - Métodos de optimización:
   - Sin restricciones (solución estática por gradiente = 0, simbólico con SymPy).
   - Gradiente descendente (numérico, configurable en código).
   - Lagrange (para restricciones de igualdad).
   - Con restricciones (general) usando SciPy `minimize` con restricciones tipo `ineq`/`eq`.
 - Comparación de métodos aplicables al problema.
 - Visualización de contornos (2D) y superficie (3D) para funciones de 2 variables.
 - Carga de problemas desde archivos `.txt` con opción de “Resolver al cargar”.
 
 ## Arquitectura (POO y módulos)
 
 - `app/optimizers.py` — Clases: `Optimizer` (base), `UnconstrainedSolver`, `GradientDescentSolver`, `LagrangeSolver`, `ConstrainedSciPySolver`.
 - `app/parsing.py` — Parseo de variables, objetivo y restricciones a SymPy/SciPy.
 - `app/plotting.py` — Gráficas 2D/3D como imágenes base64.
 - `app/ui.py` — Vista principal `OptimizerView(page)`, eventos de UI, comparador y file picker.
 - `main.py` — Punto de entrada único de la app.
 
 ## Requisitos
 
 - Python 3.9+ (recomendado 3.11 o 3.12 para mejor soporte de SciPy).
 - Dependencias en `requirements.txt`.
 
 ## Instalación
 
 ```bash
 pip install -r requirements.txt
 ```
 
 Si tu Python es 3.13 y SciPy falla al instalar, usa Python 3.11/3.12.
 
 ## Ejecución
 
 ```bash
 python main.py
 ```
 
 ## Uso de la interfaz
 
 1. Completa:
    - `Función objetivo`: notación SymPy (`x**2 + y**2`).
    - `Variables`: separadas por coma (`x,y`).
    - `Restricciones` (opcional): una por línea (`x + y - 1 = 0`, `x >= 0`).
 2. Selecciona un método y pulsa `Resolver`.
 3. `Graficar` dibuja el contorno/superficie (solo 2 variables).
 4. `Comparar métodos` muestra resultados de todos los métodos que aplican.
 5. `Cargar .txt` abre un archivo con el problema. Con el switch `Resolver al cargar` se resuelve automáticamente.
 
 ## Formato de archivos .txt
 
 Dos formatos soportados:
 
 - Etiquetado:
   ```
   objetivo: x**2 + y**2
   variables: x,y
   restricciones:
     x + y - 1 = 0
     x >= 0
   ```
 
 - Simple (3 bloques):
   ```
   x**2 + y**2
   x,y
   x + y - 1 = 0
   x >= 0
   ```
 
 ## Conjunto de ejemplos incluidos
 
 En `examples/` encontrarás problemas listos para cargar:
 
 - `01_unconstrained.txt` — f = (x-2)**2 + (y+1)**2 (sin restricciones)
 - `02_lagrange_equality.txt` — f = x**2 + y**2, con `x + y - 1 = 0`
 - `03_constrained_general.txt` — f = (x-1)**2 + (y-2)**2, con `x >= 0`, `y <= 3`
 - `04_gradient_vs_others.txt` — f = (x-3)**2 + (y+2)**2 + 0.5*(x*y), con `x >= -2`, `y >= -3`
 - `05_box_constraints_quadratic.txt` — f = (x-2)**2 + (y-1)**2, con `0 <= x <= 5`, `-1 <= y <= 4`
 - `06_distance_point_to_line.txt` — Distancia mínima del punto (3,4) a la recta `y = 2x + 1` (igualdad)
 - `07_profit_max_negative.txt` — Minimiza `-(3x + 4y - 0.5x**2 - 0.25y**2)` con `x,y >= 0`
 - `08_min_perimeter_fixed_area.txt` — Minimiza perímetro `2x + 2y` s.a. `x*y = 12`, `x,y >= 0`
 - `09_nonconvex_double_well.txt` — f = (x**2 - 1)**2 + (y - 0.5)**2 (no convexo)
 - `10_mixed_constraints.txt` — f = x**2 + y**2, con `x + y >= 1`, `x <= 2`, `y >= -1`
 
 Carga cualquiera con el botón `Cargar .txt` y presiona `Graficar` para visualizar.
 
 ## Consejos y buenas prácticas
 
 - Para métodos simbólicos (sin restricciones y Lagrange), usa funciones y restricciones expresables con SymPy.
 - Para “Con restricciones (general)”, las desigualdades se traducen a funciones `ineq` de SciPy automáticamente.
 - La gráfica solo funciona para 2 variables; para más de 2, la solución numérica/analítica sigue disponible.
 
 ## Solución de problemas
 
 - La imagen de gráfica no aparece: primero pulsa `Resolver` y luego `Graficar`. La imagen solo se muestra cuando existe un resultado válido.
 - Error instalando SciPy: usa Python 3.11/3.12 o instala ruedas compatibles para tu plataforma.
 - "Sin restricciones" no devuelve solución: puede no existir solución cerrada (gradiente=0). Prueba “Gradiente descendente” o “Con restricciones (general)”.
 
 ## Evaluación (Parcial VI)
 
 - POO: arquitectura modular por clases y módulos.
 - Métodos: sin restricciones, gradiente descendente, Lagrange (igualdad), con restricciones (general), y soporte de varias variables.
 - Interfaz sencilla, carga desde archivo y comparación de métodos.
 - Demostración en vivo: usar ejemplos de `examples/`, modificar parámetros y visualizar resultados/curvas.
