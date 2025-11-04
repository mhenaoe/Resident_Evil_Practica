# ui/menu.py
from __future__ import annotations

if __name__ in {"__main__", "__mp_main__"}:
    import os, sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Optional

from core.simulador import Simulador
from models.persona import Persona


class MenuPrincipal:

    def __init__(self) -> None:
        self.simulador: Optional[Simulador] = None

    def menu_principal(self) -> None:
        while True:
            self._mostrar_titulo()
            self._mostrar_estado_resumen()

            print("\nOpciones:")
            print(" 1) Crear simulador")
            print(" 2) Inicializar simulación")
            print(" 3) Ejecutar 1 ronda (muestra tabla de vida)")
            print(" 4) Ejecutar varias rondas (muestra tabla cada ronda)")
            print(" 5) Curar persona (x, y)")
            print(" 6) Agregar persona (x, y)")
            print(" 7) Ver matriz")
            print(" 8) Ver árbol de contagio")
            print(" 9) Ver estadísticas")
            print("10) Infectar manualmente por id (además del inicial)")
            print("11) Ver tabla de personas (vida/estado)")
            print(" 0) Salir")

            opcion = input("\nElige una opción: ").strip()

            if opcion == "1":
                self._crear_simulador()
            elif opcion == "2":
                self._inicializar()
            elif opcion == "3":
                self._ejecutar_una_ronda()
            elif opcion == "4":
                self._ejecutar_varias_rondas()
            elif opcion == "5":
                self._curar_persona()
            elif opcion == "6":
                self._agregar_persona()
            elif opcion == "7":
                self._mostrar_matriz()
            elif opcion == "8":
                self._mostrar_arbol()
            elif opcion == "9":
                self._mostrar_estadisticas()
            elif opcion == "10":
                self._infectar_por_id()
            elif opcion == "11":
                self._mostrar_tabla_personas()
            elif opcion == "0":
                print("\nHasta luego 👋")
                return
            else:
                print("Opción inválida.")
            self._esperar_enter()

    def _crear_simulador(self) -> None:
        try:
            tam = int(input("Tamaño de la matriz (N): ").strip())
            n   = int(input("Cantidad de personas: ").strip())
        except ValueError:
            print("Debes ingresar números enteros.")
            return

        txt_def = input("Defensa inicial [3]: ").strip()
        txt_seed = input("Semilla (Enter para aleatoria): ").strip()
        txt_multi = input("¿Defensa por múltiples infectados? (s/n) [n]: ").strip().lower()

        defensa_inicial = 3 if txt_def == "" else self._to_int_or(txt_def, 3)
        semilla = None if txt_seed == "" else self._to_int_or(txt_seed, None)
        usar_defensa_multiple = (txt_multi == "s")

        self.simulador = Simulador(
            tamano_matriz=tam,
            cantidad_personas=n,
            defensa_inicial=defensa_inicial,
            semilla_aleatoria=semilla,
            usar_defensa_multiple=usar_defensa_multiple
        )
        print("✅ Simulador creado.")

    def _inicializar(self) -> None:
        if not self._hay_simulador():
            return
        self.simulador.inicializar()  # type: ignore[union-attr]
        print("✅ Simulación inicializada.")
        self._mostrar_matriz()
        self._mostrar_arbol()
        self._mostrar_tabla_personas()

    def _ejecutar_una_ronda(self) -> None:
        if not self._hay_simulador_inicializado():
            return
        stats = self.simulador.ejecutar_ronda()  # type: ignore[union-attr]
        self._mostrar_stats_compactas(stats)
        self._mostrar_tabla_personas()  # <-- vida por persona tras la ronda

    def _ejecutar_varias_rondas(self) -> None:
        if not self._hay_simulador_inicializado():
            return
        try:
            k = int(input("¿Cuántas rondas quieres ejecutar?: ").strip())
        except ValueError:
            print("Debes ingresar un entero.")
            return

        k = max(0, k)
        for i in range(k):
            stats = self.simulador.ejecutar_ronda()  # type: ignore[union-attr]
            print(f"\n>>> Después de la ronda {stats.get('ronda', '?')}:")
            self._mostrar_stats_compactas(stats)
            self._mostrar_tabla_personas()  # <-- vida por persona en cada ronda

    def _curar_persona(self) -> None:
        if not self._hay_simulador_inicializado():
            return
        try:
            x = int(input("x: ").strip())
            y = int(input("y: ").strip())
        except ValueError:
            print("Debes ingresar enteros.")
            return
        ok = self.simulador.curar_persona(x, y)  # type: ignore[union-attr]
        print("✅ Persona curada." if ok else "No había persona infectada en esa celda.")

    def _agregar_persona(self) -> None:
        if not self._hay_simulador():
            return
        try:
            x = int(input("x: ").strip())
            y = int(input("y: ").strip())
        except ValueError:
            print("Debes ingresar enteros.")
            return
        ok = self.simulador.agregar_persona(x, y)  # type: ignore[union-attr]
        print("✅ Persona agregada." if ok else "No se pudo agregar la persona.")

    def _infectar_por_id(self) -> None:
        """
        Infecta manualmente a una persona por su id, además del paciente cero.
        - Si ya hay infectados, la relaciona en el árbol como contagiada por el primer infectado.
        - Si no hay infectados aún, la establece como paciente cero.
        """
        if not self._hay_simulador():
            return
        if not self.simulador.esta_inicializada:  # type: ignore[union-attr]
            print("Primero inicializa la simulación (opción 2).")
            return

        pid = input("Id de la persona (ej. p3): ").strip()
        persona = self._buscar_por_id(pid)
        if persona is None:
            print("No existe una persona con ese id.")
            return
        if persona.esta_infectada():
            print("Esa persona ya está infectada.")
            return

        infectados = self.simulador.get_personas_infectadas()  # type: ignore[union-attr]
        if len(infectados) == 0:
            # No hay paciente cero: la hacemos paciente cero
            persona.infectar(persona)
            self.simulador.get_arbol().establecer_paciente_cero(persona)  # type: ignore[union-attr]
            print(f"✅ {persona.id} ahora es paciente cero.")
        else:
            infectador = infectados[0]  # simple: el primer infectado (usualmente el paciente cero)
            persona.infectar(infectador)
            self.simulador.get_arbol().agregar_contagio(infectador, persona)  # type: ignore[union-attr]
            print(f"✅ {persona.id} infectada manualmente por {infectador.id}.")

        self._mostrar_tabla_personas()

    def _mostrar_matriz(self) -> None:
        if not self._hay_simulador():
            return
        print("\n--- MATRIZ ---")
        print(self.simulador.get_matriz().visualizar())

    def _mostrar_arbol(self) -> None:
        if not self._hay_simulador():
            return
        print("\n--- ÁRBOL DE CONTAGIO ---")
        print(self.simulador.get_arbol().visualizar())

    def _mostrar_estadisticas(self) -> None:
        if not self._hay_simulador():
            return
        stats = self.simulador.get_estadisticas()
        self._mostrar_stats_detalladas(stats)

    def _mostrar_tabla_personas(self) -> None:
        """Imprime una tabla con id, posición, defensa (vida) y estado."""
        if not self._hay_simulador():
            return
        personas = self.simulador.get_personas()
        if len(personas) == 0:
            print("\n(No hay personas)")
            return

        personas = sorted(personas, key=lambda p: p.id)

        print("\n--- PERSONAS (vida/estado) ---")
        print(f"{'ID':<5} {'POS':<9} {'DEF':>3}  {'ESTADO'}")
        print("-" * 28)
        for p in personas:
            x, y = p.get_posicion()
            estado = "INFECTADA" if p.esta_infectada() else "SANA"
            print(f"{p.id:<5} ({x:>2},{y:>2})  {p.defensa:>3}  {estado}")

    def _buscar_por_id(self, pid: str) -> Optional[Persona]:
        if not self._hay_simulador():
            return None
        for p in self.simulador.get_personas():
            if p.id == pid:
                return p
        return None

    def _mostrar_titulo(self) -> None:
        print("\n" + "=" * 60)
        print(" Resident Evil UDEM - Simulación".center(60))
        print("=" * 60)

    def _mostrar_estado_resumen(self) -> None:
        if self.simulador is None:
            print("Estado: sin simulador creado.")
            return
        ronda = self.simulador.get_ronda_actual()
        tot = len(self.simulador.get_personas())
        print(f"Estado: simulador creado | ronda={ronda} | personas={tot}")

    def _mostrar_stats_compactas(self, stats: dict) -> None:
        print(f"Ronda {stats.get('ronda', '?')}: "
              f"Sanas={stats.get('sanas', '?')}, "
              f"Infectadas={stats.get('infectadas', '?')}, "
              f"Profundidad árbol={stats.get('profundidad_arbol', '?')}")

    def _mostrar_stats_detalladas(self, stats: dict) -> None:
        print("\n--- ESTADÍSTICAS ---")
        for k in ("ronda", "total_personas", "sanas", "infectadas", "profundidad_arbol"):
            print(f"{k}: {stats.get(k)}")

    def _hay_simulador(self) -> bool:
        if self.simulador is None:
            print("Primero crea el simulador (opción 1).")
            return False
        return True

    def _hay_simulador_inicializado(self) -> bool:
        if not self._hay_simulador():
            return False
        if not self.simulador.esta_inicializada:
            print("Primero inicializa la simulación (opción 2).")
            return False
        return True

    def _to_int_or(self, texto: str, por_defecto: Optional[int]) -> Optional[int]:
        try:
            return int(texto)
        except Exception:
            return por_defecto

    def _esperar_enter(self) -> None:
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    MenuPrincipal().menu_principal()
