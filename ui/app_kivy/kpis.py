# ui/app_kivy/kpis.py
from __future__ import annotations

from typing import Dict, List
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel


class Sparkline(Widget):
    data = ListProperty([])  # valores 0..1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=lambda *_: self._redraw(), pos=lambda *_: self._redraw(), data=lambda *_: self._redraw())

    def _redraw(self):
        self.canvas.clear()
        if not self.data:
            return
        with self.canvas:
            Color(0.35, 0.75, 1.0, 1)
            n = len(self.data)
            if n < 2:
                return
            points = []
            for i, v in enumerate(self.data):
                x = self.x + (i / (n - 1)) * self.width
                y = self.y + v * self.height
                points.extend([x, y])
            Line(points=points, width=1.2)


class KPIsWidget(MDCard):
    """Tarjetas KPI + sparkline de infectados."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = dp(14)
        self.padding = dp(10)
        self.md_bg_color = (0.12, 0.12, 0.12, 1)
        self.series_infectados: List[float] = []

        self.lbl_ronda = MDLabel(text="Ronda: -", halign="left")
        self.lbl_tot = MDLabel(text="Personas: -", halign="left")
        self.lbl_sanas = MDLabel(text="Sanas: -", halign="left")
        self.lbl_inf = MDLabel(text="Infectadas: -", halign="left")
        self.lbl_prof = MDLabel(text="Profundidad árbol: -", halign="left")

        self.spark = Sparkline(size_hint_y=None, height=dp(48))

        box = MDBoxLayout(orientation="vertical", spacing=dp(6))
        row1 = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(24))
        row1.add_widget(self.lbl_ronda)
        row1.add_widget(self.lbl_prof)

        row2 = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(24))
        row2.add_widget(self.lbl_tot)
        row2.add_widget(self.lbl_sanas)
        row2.add_widget(self.lbl_inf)

        box.add_widget(row1)
        box.add_widget(row2)
        box.add_widget(self.spark)
        self.add_widget(box)

    def reset_series(self) -> None:
        self.series_infectados = []
        self.spark.data = []

    def update_stats(self, stats: Dict[str, int]) -> None:
        if not stats:
            return
        self.lbl_ronda.text = f"Ronda: {stats.get('ronda', '-')}"
        self.lbl_tot.text = f"Personas: {stats.get('total_personas', '-')}"
        self.lbl_sanas.text = f"Sanas: {stats.get('sanas', '-')}"
        self.lbl_inf.text = f"Infectadas: {stats.get('infectadas', '-')}"
        self.lbl_prof.text = f"Profundidad árbol: {stats.get('profundidad_arbol', '-')}"

        # sparkline normalizada por total
        tot = max(1, int(stats.get('total_personas', 1)))
        inf = int(stats.get('infectadas', 0))
        ratio = max(0.0, min(1.0, inf / tot))
        self.series_infectados.append(ratio)
        # muestra últimos 80 puntos
        self.series_infectados = self.series_infectados[-80:]
        self.spark.data = self.series_infectados[:]
