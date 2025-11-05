# ui/app_kivy/main_kivy.py
from __future__ import annotations

# --- permitir ejecutar como módulo: python -m ui.app_kivy.main_kivy
import os, sys, time
if __name__ in {"__main__", "__mp_main__"}:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from typing import Optional, Dict, Any, List

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatIconButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine

# Top bar: alias para versiones antiguas
try:
    from kivymd.uix.toolbar import MDTopAppBar
except Exception:
    from kivymd.uix.toolbar import MDToolbar as MDTopAppBar

from core.simulador import Simulador
from ui.app_kivy.board import BoardWidget
from ui.app_kivy.kpis import KPIsWidget
from ui.app_kivy.tree import open_tree_dialog


# --- utilidades UI ---
def make_hint(text: str) -> MDLabel:
    return MDLabel(
        text=text,
        theme_text_color="Hint",
        halign="left",
        size_hint_y=None,
        height=dp(18),
    )


# ==================== CONTROLADOR ====================
class SimulationController:
    """Conecta el motor (Simulador) con la UI y el reloj de animación."""
    def __init__(self) -> None:
        self.sim: Optional[Simulador] = None
        self._event = None
        self.rounds_per_sec: float = 2.0
        self.on_after_step = None  # callback(stats: dict[str, Any]) -> None

    # Motor
    def new_simulation(self, n_grid: int, n_people: int, defensa: int,
                       semilla: Optional[int], multidaño: bool) -> None:
        self.stop()
        self.sim = Simulador(
            tamano_matriz=n_grid,
            cantidad_personas=n_people,
            defensa_inicial=defensa,
            semilla_aleatoria=semilla,
            usar_defensa_multiple=multidaño
        )
        self.sim.inicializar()

    def step(self) -> Dict[str, Any]:
        if not self.sim:
            return {}
        stats = self.sim.ejecutar_ronda()
        if self.on_after_step:
            self.on_after_step(stats)
        return stats

    def play(self) -> None:
        if not self.sim:
            return
        self.stop()
        interval = 1.0 / max(0.1, self.rounds_per_sec)
        self._event = Clock.schedule_interval(lambda dt: self.step(), interval)

    def pause(self) -> None:
        self.stop()

    def stop(self) -> None:
        if self._event is not None:
            self._event.cancel()
            self._event = None

    def set_speed(self, rps: float) -> None:
        """Actualiza la velocidad y reinicia el scheduler si está corriendo."""
        self.rounds_per_sec = max(0.1, rps)
        if self._event is not None:
            # reprogramar con el nuevo intervalo
            self.play()

    # API para la UI
    def grid_size(self) -> int:
        return self.sim.get_matriz().get_tamano() if self.sim else 0

    def persons_snapshot(self) -> List[Dict[str, Any]]:
        if not self.sim:
            return []
        data: List[Dict[str, Any]] = []
        for p in self.sim.get_personas():
            x, y = p.get_posicion()
            data.append({"id": p.id, "x": x, "y": y, "infected": p.esta_infectada(), "defensa": p.defensa})
        return data

    def stats(self) -> Dict[str, Any]:
        return self.sim.get_estadisticas() if self.sim else {}

    def tree_text(self) -> str:
        return self.sim.get_arbol().visualizar() if self.sim else "(sin árbol)"

    def curar_at(self, x: int, y: int) -> bool:
        return self.sim.curar_persona(persona_x := x, persona_y := y) if self.sim else False  # noqa

    def agregar_at(self, x: int, y: int) -> bool:
        return self.sim.agregar_persona(x, y) if self.sim else False

    def infectar_en_celda(self, x: int, y: int) -> bool:
        if not self.sim:
            return False
        personas = self.sim.get_matriz().obtener_personas_en(x, y)
        if not personas:
            return False
        sanas = [p for p in personas if not p.esta_infectada()]
        if not sanas:
            return False

        objetivo = min(sanas, key=lambda p: p.defensa)
        global_infect = self.sim.get_personas_infectadas()
        if len(global_infect) == 0:
            objetivo.infectar(objetivo)
            self.sim.get_arbol().establecer_paciente_cero(objetivo)
            return True

        infectador = global_infect[0]
        objetivo.infectar(infectador)
        self.sim.get_arbol().agregar_contagio(infectador, objetivo)
        return True


# ==================== PANEL LATERAL ====================
class ControlPanel(MDCard):
    controller: SimulationController
    board: BoardWidget
    kpis: KPIsWidget

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = dp(12)
        self.size_hint_x = 0.36
        self.radius = dp(16)
        self.md_bg_color = (18/255, 18/255, 18/255, 1)

        # ---------- contenidos de cada panel ----------
        # PARÁMETROS
        self.txt_n = MDTextField(text="20", hint_text="Tamaño matriz (N)", mode="rectangle")
        self.txt_p = MDTextField(text="60", hint_text="Número de personas", mode="rectangle")
        self.txt_def = MDTextField(text="3", hint_text="Defensa inicial", mode="rectangle")
        self.txt_seed = MDTextField(text="", hint_text="Semilla (opcional)", mode="rectangle")
        self.sw_multi = MDSwitch(active=False)
        row_multi = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(34))
        row_multi.add_widget(self.sw_multi)
        row_multi.add_widget(MDLabel(text="Daño múltiple (−1 por infectado en la celda)", halign="left"))

        params_box = MDBoxLayout(orientation="vertical", spacing=dp(10),
                                 padding=(dp(8), 0, dp(8), dp(8)), adaptive_height=True)
        params_box.add_widget(make_hint("Configura y crea una nueva simulación."))
        params_box.add_widget(self.txt_n)
        params_box.add_widget(self.txt_p)
        params_box.add_widget(self.txt_def)
        params_box.add_widget(self.txt_seed)
        params_box.add_widget(row_multi)
        self.btn_new = MDFillRoundFlatIconButton(text="Nueva simulación", icon="reload",
                                                 on_release=lambda *_: self._on_new())
        params_box.add_widget(self.btn_new)

        # CONTROLES
        controls_box = MDBoxLayout(orientation="vertical", spacing=dp(10),
                                   padding=(dp(8), 0, dp(8), dp(8)), adaptive_height=True)
        controls_box.add_widget(make_hint("Ejecuta la simulación y ajusta la velocidad."))
        toolbar = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(44))
        self.btn_play = MDIconButton(icon="play", on_release=lambda *_: self._on_play())
        self.btn_pause = MDIconButton(icon="pause", on_release=lambda *_: self._on_pause())
        self.btn_step = MDIconButton(icon="skip-next", on_release=lambda *_: self._on_step())
        toolbar.add_widget(self.btn_play); toolbar.add_widget(self.btn_pause); toolbar.add_widget(self.btn_step)
        controls_box.add_widget(toolbar)

        # fila de velocidad: −  [ Velocidad: 1.5 r/s ]  slider  +
        row_speed = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                                size_hint_y=None, height=dp(42))
        self.btn_minus = MDIconButton(icon="minus", on_release=lambda *_: self._bump_speed(-0.5))
        self.lbl_speed = MDLabel(text="Velocidad: 2.0 r/s",
                                 halign="center", size_hint_x=None, width=dp(160))
        self.slider_speed = MDSlider(min=0.5, max=20, value=2.0, step=0.5)
        self.slider_speed.bind(value=self._on_speed_change)
        self.btn_plus = MDIconButton(icon="plus", on_release=lambda *_: self._bump_speed(+0.5))
        row_speed.add_widget(self.btn_minus)
        row_speed.add_widget(self.lbl_speed)
        row_speed.add_widget(self.slider_speed)
        row_speed.add_widget(self.btn_plus)
        controls_box.add_widget(row_speed)

        # INDICADORES
        self.kpis = KPIsWidget()
        self.kpis.size_hint_y = None
        self.kpis.height = dp(260)  # más alto para evitar solapes
        indicadores_box = MDBoxLayout(orientation="vertical", spacing=dp(6),
                                      padding=(dp(8), 0, dp(8), dp(8)), adaptive_height=True)
        indicadores_box.add_widget(make_hint("Resumen de la ronda actual y evolución."))
        indicadores_box.add_widget(self.kpis)

        # HERRAMIENTAS
        tools_box = MDBoxLayout(orientation="vertical", spacing=dp(10),
                                padding=(dp(8), 0, dp(8), dp(8)), adaptive_height=True)
        tools_box.add_widget(make_hint("Acciones rápidas sobre el tablero y visualizaciones."))

        row_tools_1 = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                                  size_hint_y=None, height=dp(40))
        row_tools_1.add_widget(MDFillRoundFlatIconButton(text="Ver árbol", icon="source-branch",
                               on_release=lambda *_: self._show_tree()))
        row_tools_1.add_widget(MDFillRoundFlatIconButton(text="Tabla de salud", icon="table",
                               on_release=lambda *_: self._open_health_table()))
        tools_box.add_widget(row_tools_1)

        row_tools_2 = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                                  size_hint_y=None, height=dp(40))
        row_tools_2.add_widget(MDFillRoundFlatIconButton(text="Infectar celda", icon="virus",
                               on_release=lambda *_: self._mode('infect')))
        row_tools_2.add_widget(MDFillRoundFlatIconButton(text="Curar celda", icon="account-heart",
                               on_release=lambda *_: self._mode('cure')))
        tools_box.add_widget(row_tools_2)

        row_tools_3 = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                                  size_hint_y=None, height=dp(40))
        row_tools_3.add_widget(MDFillRoundFlatIconButton(text="Agregar persona", icon="account-plus",
                               on_release=lambda *_: self._mode('add')))
        row_tools_3.add_widget(MDFillRoundFlatIconButton(text="Capturar tablero", icon="camera",
                               on_release=lambda *_: self._snapshot_board()))
        tools_box.add_widget(row_tools_3)

        # ---------- panels desplegables ----------
        self.root_stack = MDBoxLayout(orientation="vertical", spacing=dp(12))
        self.root_stack.add_widget(MDExpansionPanel(
            icon="tune",
            panel_cls=MDExpansionPanelOneLine(text="Parámetros (configurar nueva simulación)"),
            content=params_box,
        ))
        self.root_stack.add_widget(MDExpansionPanel(
            icon="controller-classic",
            panel_cls=MDExpansionPanelOneLine(text="Controles (play / pausa / paso / velocidad)"),
            content=controls_box,
        ))
        self.root_stack.add_widget(MDExpansionPanel(
            icon="chart-areaspline",
            panel_cls=MDExpansionPanelOneLine(text="Indicadores (KPIs de la simulación)"),
            content=indicadores_box,
        ))
        self.root_stack.add_widget(MDExpansionPanel(
            icon="tools",
            panel_cls=MDExpansionPanelOneLine(text="Herramientas (acciones rápidas)"),
            content=tools_box,
        ))

        self.add_widget(self.root_stack)

    # ------- helpers velocidad -------
    def _on_speed_change(self, _slider, value: float) -> None:
        # actualiza la etiqueta y la velocidad del motor
        v = float(value)
        self.lbl_speed.text = f"Velocidad: {v:.1f} r/s"
        self.controller.set_speed(v)

    def _bump_speed(self, delta: float) -> None:
        v = self.slider_speed.value + delta
        v = max(self.slider_speed.min, min(self.slider_speed.max, v))
        # asignar al slider dispara _on_speed_change
        self.slider_speed.value = v

    # ------- acciones de herramientas -------
    def _show_tree(self) -> None:
        txt = self.controller.tree_text() if self.controller.sim else "(sin árbol)"
        open_tree_dialog(txt)

    def _open_health_table(self) -> None:
        if not self.controller.sim:
            MDDialog(title="Aviso", text="Crea una simulación primero.").open()
            return

        rows = []
        for d in self.controller.persons_snapshot():
            estado = "INFECTADA" if d["infected"] else "SANA"
            rows.append((d["id"], str(d["defensa"]), estado, str(d["x"]), str(d["y"])))

        wrapper = MDBoxLayout(orientation="vertical", size_hint=(0.95, None),
                              height=dp(420), padding=(dp(6), 0, dp(6), dp(6)))
        scroll = MDScrollView(size_hint=(1, 1))
        wrapper.add_widget(scroll)

        grid = GridLayout(cols=5, size_hint_y=None, size_hint_x=1, padding=dp(8), spacing=dp(10))
        grid.bind(minimum_height=grid.setter("height"))

        def H(txt):  # header
            return MDLabel(text=f"[b]{txt}[/b]", markup=True, halign="left",
                           size_hint_y=None, height=dp(26))
        def C(txt):  # cell
            return MDLabel(text=txt, halign="left", size_hint_y=None, height=dp(24))

        for h in ("ID", "Defensa", "Estado", "X", "Y"):
            grid.add_widget(H(h))

        for rid, defn, est, xs, ys in rows:
            grid.add_widget(C(rid));  grid.add_widget(C(defn))
            grid.add_widget(C(est));  grid.add_widget(C(xs))
            grid.add_widget(C(ys))

        scroll.add_widget(grid)

        dlg = None
        dlg = MDDialog(
            title="Tabla de salud (personas)",
            type="custom",
            content_cls=wrapper,
            buttons=[MDFillRoundFlatIconButton(text="Cerrar", icon="close",
                                               on_release=lambda *_: dlg.dismiss())],
        )
        dlg.open()

    def _snapshot_board(self) -> None:
        os.makedirs("screenshots", exist_ok=True)
        path = os.path.join("screenshots", f"tablero_{int(time.time())}.png")
        self.board.export_to_png(path)
        MDDialog(title="Captura guardada", text=f"Imagen en {path}").open()

    def _mode(self, new_mode: str) -> None:
        if not hasattr(self, "parent"):
            return
        root: RootLayout = self.parent.parent  # Body -> ControlPanel
        root.mode = new_mode
        root._toast(f"Modo: {new_mode}" if new_mode != "add" else "Modo: agregar persona")

    # ------- callbacks de simulación -------
    def _on_new(self) -> None:
        try:
            n = max(2, int(self.txt_n.text.strip()))      # permite 2x2
            p = max(1, int(self.txt_p.text.strip()))
            d = max(0, int(self.txt_def.text.strip()))
            seed_txt = self.txt_seed.text.strip()
            seed = int(seed_txt) if seed_txt else None
            mult = bool(self.sw_multi.active)
        except Exception:
            MDDialog(title="Error", text="Revisa los parámetros (enteros válidos).").open()
            return

        self.controller.new_simulation(n, p, d, seed, mult)
        self.board.configure_grid(n)
        self.board.update_people(self.controller.persons_snapshot())
        self.kpis.reset_series()
        self.kpis.update_stats(self.controller.stats())
        MDDialog(title="Simulación", text="Simulación inicializada.").open()

    def _on_play(self) -> None:
        if not self.controller.sim:
            MDDialog(title="Aviso", text="Crea una simulación primero.").open()
            return
        self.controller.play()

    def _on_pause(self) -> None:
        self.controller.pause()

    def _on_step(self) -> None:
        if not self.controller.sim:
            MDDialog(title="Aviso", text="Crea una simulación primero.").open()
            return
        stats = self.controller.step()
        self.board.update_people(self.controller.persons_snapshot())
        self.kpis.update_stats(stats)


# ==================== LAYOUT RAÍZ ====================
class RootLayout(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.controller = SimulationController()

        # App Bar
        self.topbar = MDTopAppBar(title="Resident Evil UDEM — Simulación", elevation=4, pos_hint={"top": 1})
        self.topbar.right_action_items = [
            ["crosshairs", lambda *_: self._toggle_add()],
            ["virus", lambda *_: self._infect_mode()],
            ["account-heart", lambda *_: self._cure_mode()],
            ["source-branch", lambda *_: self._show_tree()],
        ]
        self.add_widget(self.topbar)

        # Cuerpo: tablero + panel
        body = MDBoxLayout(orientation="horizontal", spacing=dp(8), padding=dp(8))
        self.board = BoardWidget(on_cell_action=self._on_board_action)
        self.board.size_hint_x = 0.64

        self.panel = ControlPanel()
        self.panel.controller = self.controller
        self.panel.board = self.board

        body.add_widget(self.board)
        body.add_widget(self.panel)
        self.add_widget(body)

        # callback post-step
        self.controller.on_after_step = self._after_step

        # modos de acción del tablero
        self.mode: str = "select"   # select | add | infect | cure
        Window.bind(on_key_down=self._on_key)

    # --- acciones tablero ---
    def _on_board_action(self, x: int, y: int) -> None:
        if not self.controller.sim:
            return
        ok = False
        if self.mode == "infect":
            ok = self.controller.infectar_en_celda(x, y)
        elif self.mode == "cure":
            ok = self.controller.curar_at(x, y)
        elif self.mode == "add":
            ok = self.controller.agregar_at(x, y)

        if ok:
            self.board.update_people(self.controller.persons_snapshot())
            self.panel.kpis.update_stats(self.controller.stats())
        else:
            MDDialog(title="Sin acción", text=f"No se pudo aplicar acción en ({x}, {y}).").open()

    def _after_step(self, stats: Dict[str, Any]) -> None:
        self.board.update_people(self.controller.persons_snapshot())
        self.panel.kpis.update_stats(stats)

    # --- acciones topbar ---
    def _toggle_add(self) -> None:
        self.mode = "add" if self.mode != "add" else "select"
        self._toast(f"Modo: {'Agregar' if self.mode=='add' else 'Seleccionar'}")

    def _infect_mode(self) -> None:
        self.mode = "infect"
        self._toast("Modo: Infectar (clic en celda)")

    def _cure_mode(self) -> None:
        self.mode = "cure"
        self._toast("Modo: Curar (clic en celda)")

    def _show_tree(self) -> None:
        txt = self.controller.tree_text() if self.controller.sim else "(sin árbol)"
        open_tree_dialog(txt)

    # --- utilidades ---
    def _toast(self, msg: str) -> None:
        MDDialog(title="Modo", text=msg).open()

    def _on_key(self, _window, key, _scancode, _codepoint, _modifiers):
        # SPACE = play/pause, → = step
        if key == 32:
            if self.controller._event:
                self.controller.pause()
                self._toast("Pause")
            else:
                self.controller.play()
                self._toast("Play")
            return True
        if key == 262:
            # Flecha derecha
            self.panel._on_step()
            return True
        return False


# ==================== APP ====================
class ResidentEvilApp(MDApp):
    def build(self):
        self.title = "Resident Evil UDEM — Feria"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        return RootLayout()


if __name__ == "__main__":
    ResidentEvilApp().run()
