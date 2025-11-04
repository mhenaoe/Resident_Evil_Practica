from __future__ import annotations  

import random
from typing import Optional, Any

from models.persona import Persona
from models.nodo_arbol import NodoArbol
from models.matriz import Matriz
from models.arbol_contagio import ArbolContagio

    
class Simulador:

    def __init__(self, tamano_matriz: int, cantidad_personas: int,
                 defensa_inicial: int = 3, semilla_aleatoria: Optional[int] = None,
                 usar_defensa_multiple: bool = False) -> None:

        self.tamano_matriz: int = tamano_matriz
        self.cantidad_personas_inicial: int = cantidad_personas
        self.defensa_inicial: int = defensa_inicial
        self.semilla_aleatoria: Optional[int] = semilla_aleatoria
        self.usar_defensa_multiple: bool = usar_defensa_multiple

        if self.semilla_aleatoria is not None:
            random.seed(self.semilla_aleatoria)

        self.matriz: Matriz = Matriz(tamano_matriz)
        self.arbol: ArbolContagio = ArbolContagio()
        self.lista_personas: list[Persona] = []
        self.ronda_actual: int = 0
        self.contador_personas: int = 0
        self.esta_inicializada: bool = False

    def inicializar(self) -> None:
        if self.semilla_aleatoria is not None:
            random.seed(self.semilla_aleatoria)

        self._generar_personas_aleatorias()
        self._seleccionar_paciente_cero()
        self.esta_inicializada = True

    def ejecutar_ronda(self) -> dict[str, Any]:
        if not self.esta_inicializada:
            return {}

        self.ronda_actual = self.ronda_actual + 1

        self._mover_todas_personas()
        self._verificar_contagios()

        if self.ronda_actual % 3 == 0:
            self._aplicar_aumento_defensa()

        estadisticas = self.get_estadisticas()
        return estadisticas

    def _generar_personas_aleatorias(self) -> None:
        posiciones_ocupadas = set()

        for i in range(self.cantidad_personas_inicial):
            while True:
                x_aleatorio = random.randint(0, self.tamano_matriz - 1)
                y_aleatorio = random.randint(0, self.tamano_matriz - 1)

                posicion = (x_aleatorio, y_aleatorio)

                if posicion not in posiciones_ocupadas:
                    posiciones_ocupadas.add(posicion)
                    break

            self.contador_personas = self.contador_personas + 1
            id_persona = f"p{self.contador_personas}"

            persona_nueva = Persona(id_persona, x_aleatorio, y_aleatorio, self.defensa_inicial)
            self.matriz.agregar_persona(persona_nueva)
            self.lista_personas.append(persona_nueva)

    def _seleccionar_paciente_cero(self) -> None:
        paciente_cero = random.choice(self.lista_personas)
        paciente_cero.infectar(paciente_cero)
        self.arbol.establecer_paciente_cero(paciente_cero)

    def _mover_todas_personas(self) -> None:
        for persona in self.lista_personas:
            dx, dy = self._obtener_direccion_aleatoria()

            x_actual, y_actual = persona.get_posicion()
            x_nueva = x_actual + dx
            y_nueva = y_actual + dy

            self.matriz.mover_persona(persona, x_nueva, y_nueva)

    def _obtener_direccion_aleatoria(self) -> tuple[int, int]:
        lista_direcciones = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        direccion_elegida = random.choice(lista_direcciones)
        return direccion_elegida

    def _verificar_contagios(self) -> None:
        celdas_ocupadas = self.matriz.get_celdas_ocupadas()

        for x, y in celdas_ocupadas:
            if self.matriz.hay_multiple_personas(x, y):
                self._procesar_celda_con_cruces(x, y)

    def _procesar_celda_con_cruces(self, x: int, y: int) -> None:
        personas_en_celda = self.matriz.obtener_personas_en(x, y)

        lista_sanas = []
        lista_infectadas = []

        for persona in personas_en_celda:
            if persona.esta_infectada():
                lista_infectadas.append(persona)
            else:
                lista_sanas.append(persona)

        cantidad_sanas = len(lista_sanas)
        cantidad_infectadas = len(lista_infectadas)

        if cantidad_sanas > 0 and cantidad_infectadas > 0:
            for persona_sana in lista_sanas:

                if self.usar_defensa_multiple:
                    for i in range(cantidad_infectadas):
                        persona_sana.reducir_defensa()
                else:
                    persona_sana.reducir_defensa()

                if persona_sana.defensa == 0 and not persona_sana.esta_infectada():
                    infectador_elegido = random.choice(lista_infectadas)
                    persona_sana.infectar(infectador_elegido)
                    self.arbol.agregar_contagio(infectador_elegido, persona_sana)

    def _aplicar_aumento_defensa(self) -> None:
        for persona in self.lista_personas:
            if not persona.esta_infectada():
                persona.aumentar_defensa()

    def curar_persona(self, x: int, y: int) -> bool:
        personas_en_celda = self.matriz.obtener_personas_en(x, y)

        for persona in personas_en_celda:
            if persona.esta_infectada():
                self.arbol.curar_persona(persona)
                return True

        return False

    def agregar_persona(self, x: int, y: int) -> bool:
        self.contador_personas = self.contador_personas + 1
        id_nuevo = f"p{self.contador_personas}"

        persona_nueva = Persona(id_nuevo, x, y, self.defensa_inicial)
        self.matriz.agregar_persona(persona_nueva)
        self.lista_personas.append(persona_nueva)

        return True

    def todas_infectadas(self) -> bool:
        for persona in self.lista_personas:
            if not persona.esta_infectada():
                return False
        return True

    def get_estadisticas(self) -> dict[str, Any]:
        cantidad_total = len(self.lista_personas)
        cantidad_infectadas = len(self.arbol.get_infectados())
        cantidad_sanas = cantidad_total - cantidad_infectadas
        profundidad_arbol = self.arbol.get_profundidad()

        estadisticas = {
            'ronda': self.ronda_actual,
            'total_personas': cantidad_total,
            'sanas': cantidad_sanas,
            'infectadas': cantidad_infectadas,
            'profundidad_arbol': profundidad_arbol
        }

        return estadisticas

    def get_ronda_actual(self) -> int:
        return self.ronda_actual

    def get_matriz(self) -> Matriz:
        return self.matriz

    def get_arbol(self) -> ArbolContagio:
        return self.arbol

    def get_personas(self) -> list[Persona]:
        return self.lista_personas

    def get_personas_sanas(self) -> list[Persona]:
        lista_sanas = []
        for persona in self.lista_personas:
            if not persona.esta_infectada():
                lista_sanas.append(persona)
        return lista_sanas

    def get_personas_infectadas(self) -> list[Persona]:
        return self.arbol.get_infectados()


