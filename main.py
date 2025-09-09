import os
import flet as ft
from app.ui import OptimizerView


def main(page: ft.Page):
    page.title = "Calculadora Optimización No Lineal"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.colors.TEAL, use_material3=True)
    page.bgcolor = ft.colors.GREY_50

    # Handlers UI (tema y README)
    def toggle_dark(e: ft.ControlEvent):
        page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        page.update()

    def set_palette(color: str):
        page.theme = ft.Theme(color_scheme_seed=color, use_material3=True)
        page.update()

    def open_readme(e):
        # Construir ruta absoluta al README.md
        readme_path = os.path.abspath(os.path.join(os.getcwd(), "README.md"))
        page.launch_url(f"file:///{readme_path}")

    dark_switch = ft.Switch(label="Modo oscuro", value=False, on_change=toggle_dark)
    palette_menu = ft.PopupMenuButton(
        tooltip="Paleta de color",
        icon=ft.Icons.PALETTE_OUTLINED,
        items=[
            ft.PopupMenuItem(text="Turquesa", on_click=lambda e: set_palette(ft.colors.TEAL)),
            ft.PopupMenuItem(text="Azul", on_click=lambda e: set_palette(ft.colors.BLUE)),
            ft.PopupMenuItem(text="Verde", on_click=lambda e: set_palette(ft.colors.GREEN)),
            ft.PopupMenuItem(text="Morado", on_click=lambda e: set_palette(ft.colors.DEEP_PURPLE)),
            ft.PopupMenuItem(text="Ámbar", on_click=lambda e: set_palette(ft.colors.AMBER)),
            ft.PopupMenuItem(text="Rosa", on_click=lambda e: set_palette(ft.colors.PINK)),
        ],
    )

    page.appbar = ft.AppBar(
        title=ft.Text("Calculadora de Optimización No Lineal", weight=ft.FontWeight.BOLD),
        bgcolor=ft.colors.SURFACE,
        center_title=False,
        actions=[
            palette_menu,
            dark_switch,
            ft.IconButton(ft.Icons.ARTICLE_OUTLINED, tooltip="Abrir README", on_click=open_readme),
        ],
    )

    page.add(OptimizerView(page))


if __name__ == "__main__":
    ft.app(target=main)
