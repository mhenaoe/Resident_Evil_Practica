# ui/app_kivy/board.py
from __future__ import annotations

from typing import Callable, List, Dict
from math import sin
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp


class BoardWidget(Widget):
    """Tablero 2D con grid y personas (animación de pulso en infectados)."""
    grid_size = NumericProperty(0)
    people: List[Dict] = ListProperty([])  # cada item: {"id","x","y","infected","defensa"}
    on_cell_action: Callable[[int, int], None] = ObjectProperty(None, allownone=True)

    def __init__(self, on_cell_action: Callable[[int, int], None] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.on_cell_action = on_cell_action
        self._anim_t = 0.0
        self._clock = Clock.schedule_interval(self._tick, 1 / 30.0)  # 30 FPS
        self.bind(size=lambda *_: self._redraw(), pos=lambda *_: self._redraw())
        self._bg_color = (0.08, 0.08, 0.08, 1)

    # --------- API ----------
    def configure_grid(self, n: int) -> None:
        self.grid_size = int(n)
        self._redraw()

    def update_people(self, people: List[Dict]) -> None:
        self.people = people
        self._redraw()

    # --------- Animación ----------
    def _tick(self, dt: float) -> None:
        self._anim_t = (self._anim_t + dt) % 1000
        if self.people:
            self._redraw_dynamic()

    # --------- Render ----------
    def _cell_rect(self, x: int, y: int):
        if self.grid_size <= 0:
            return 0, 0, 0, 0
        cw = self.width / self.grid_size
        ch = self.height / self.grid_size
        return (self.x + x * cw, self.y + y * ch, cw, ch)

    def _redraw(self) -> None:
        self.canvas.clear()
        with self.canvas:
            Color(*self._bg_color)
            Rectangle(pos=self.pos, size=self.size)

            # Grid
            if self.grid_size > 0:
                Color(0.18, 0.18, 0.18, 1)
                for i in range(self.grid_size + 1):
                    # vertical
                    x = self.x + i * (self.width / self.grid_size)
                    Line(points=[x, self.y, x, self.top], width=1)
                    # horizontal
                    y = self.y + i * (self.height / self.grid_size)
                    Line(points=[self.x, y, self.right, y], width=1)

            # Personas (estático; el pulso se renderiza en _redraw_dynamic)
            for p in self.people:
                self._draw_person(p, pulsing=False)

    def _redraw_dynamic(self) -> None:
        # Solo re-dibuja las “capas” de personas (encima del grid)
        self._redraw()  # por simplicidad; si necesitas más rendimiento, separa en grupos canvas

        # Añade pulso sobre infectados
        with self.canvas:
            for p in self.people:
                if p.get("infected"):
                    self._draw_person(p, pulsing=True)

    def _draw_person(self, p: Dict, pulsing: bool) -> None:
        x, y = int(p["x"]), int(p["y"])
        cx, cy, cw, ch = self._cell_rect(x, y)
        r = min(cw, ch) * 0.32
        cxm, cym = cx + cw / 2, cy + ch / 2

        if p.get("infected"):
            base = (0.9, 0.2, 0.2, 1)  # rojo
        else:
            base = (0.2, 0.8, 0.35, 1)  # verde

        if pulsing:
            k = (sin(self._anim_t * 4.0) + 1.0) * 0.5  # 0..1
            rr = r * (1.0 + 0.25 * k)
            Color(*base)
            Ellipse(pos=(cxm - rr, cym - rr), size=(2 * rr, 2 * rr))
        else:
            Color(*base)
            Ellipse(pos=(cxm - r, cym - r), size=(2 * r, 2 * r))

        # defensa “barra” breve
        def_val = int(p.get("defensa", 0))
        Color(0.6, 0.6, 0.6, 1)
        bw = cw * 0.6
        bh = dp(3)
        bx = cxm - bw / 2
        by = cy + ch * 0.1
        Rectangle(pos=(bx, by), size=(bw, bh))
        # fill defensa (capado a 5 para visual)
        fill = max(0.0, min(1.0, def_val / 5.0))
        Color(0.2, 0.7, 1.0, 1) if not p.get("infected") else Color(1.0, 0.4, 0.4, 1)
        Rectangle(pos=(bx, by), size=(bw * fill, bh))

    # --------- Interacción ----------
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        if self.grid_size <= 0:
            return True
        cw = self.width / self.grid_size
        ch = self.height / self.grid_size
        gx = int((touch.x - self.x) // cw)
        gy = int((touch.y - self.y) // ch)
        if self.on_cell_action:
            self.on_cell_action(gx, gy)
        return True
