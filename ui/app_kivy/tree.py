# ui/app_kivy/tree.py
from __future__ import annotations
import os, time
from typing import Tuple
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.resources import resource_find
from kivy.core.text import LabelBase

from kivy.uix.codeinput import CodeInput
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDFillRoundFlatIconButton

# Registrar fuente monoespaciada (viene con Kivy)
try:
    mono_path = resource_find("data/fonts/DroidSansMono.ttf")
    if mono_path:
        LabelBase.register(name="Mono", fn_regular=mono_path)
        MONO = "Mono"
    else:
        MONO = "Roboto"  # fallback
except Exception:
    MONO = "Roboto"

def _normalize(text: str) -> str:
    """
    Asegura que no vengan caracteres raros; si tu visualizador usa ASCII,
    reemplaza box-drawing por equivalentes ASCII.
    """
    return (text.replace("│", "|")
                .replace("─", "-")
                .replace("└", "`-")
                .replace("├", "+-"))

def _wrap_tree_text(raw: str) -> str:
    raw = raw.strip("\n")
    if not raw:
        return "(árbol vacío)"
    title = "ÁRBOL DE PROPAGACIÓN"
    lines = raw.splitlines()
    width = max(len(title), *(len(l) for l in lines))
    width = max(20, min(120, width))
    bar = "─" * width
    return f"{title}\n{bar}\n{raw}\n"

def _build_tree_widget(text: str) -> Tuple[MDScrollView, CodeInput]:
    pretty = _wrap_tree_text(text)
    scroll = MDScrollView(do_scroll_x=True, do_scroll_y=True,
                          size_hint=(0.95, None), height=dp(520))
    code = CodeInput(text=pretty, readonly=True, font_name=MONO,
                     size_hint=(1, None), height=dp(520),
                     background_color=(0, 0, 0, 0),  # transparente
                     foreground_color=(1, 1, 1, 1))
    scroll.add_widget(code)
    return scroll, code

def open_tree_dialog(text: str) -> None:
    content, code = _build_tree_widget(_normalize(text))
    dlg = None

    def save_png(*_):
        os.makedirs("screenshots", exist_ok=True)
        path = os.path.join("screenshots", f"arbol_{int(time.time())}.png")

        # Espera un frame para que exista un FBO válido
        def _do_save(_dt):
            try:
                content.canvas.ask_update()
                content.export_to_png(path)
                MDDialog(title="Guardado", text=f"Árbol guardado en:\n{path}").open()
            except Exception:
                # Fallback: captura ventana completa si el widget falla
                Window.screenshot(name=path)
                MDDialog(title="Guardado (fallback)",
                         text=f"No se pudo exportar el widget.\nSe guardó la ventana en:\n{path}").open()
        Clock.schedule_once(_do_save, 0.05)

    def copy_text(*_):
        Clipboard.copy(code.text)
        MDDialog(title="Copiado", text="El árbol se copió al portapapeles.").open()

    def save_txt(*_):
        os.makedirs("screenshots", exist_ok=True)
        path = os.path.join("screenshots", f"arbol_{int(time.time())}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code.text)
        MDDialog(title="Guardado", text=f"Archivo de texto guardado en:\n{path}").open()

    dlg = MDDialog(
        title="Árbol de contagio",
        type="custom",
        content_cls=content,
        buttons=[
            MDFillRoundFlatIconButton(text="Guardar PNG", icon="content-save", on_release=save_png),
            MDFillRoundFlatIconButton(text="Copiar", icon="content-copy", on_release=copy_text),
            MDFillRoundFlatIconButton(text="Guardar TXT", icon="file-document", on_release=save_txt),
            MDFillRoundFlatIconButton(text="Cerrar", icon="close", on_release=lambda *_: dlg.dismiss()),
        ],
    )
    dlg.open()
