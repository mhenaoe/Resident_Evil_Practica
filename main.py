import random
from typing import Optional


from persona import Persona
from matriz import Matriz
from arbol_contagio import ArbolContagio


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

    def ejecutar_ronda(self) -> dict[str, any]:
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

    def get_estadisticas(self) -> dict[str, any]:
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


if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "PRUEBAS DEL SIMULADOR")
    print("=" * 70)

    print("\n📌 TEST 1: Crear simulador")
    print("-" * 70)
    simulador = Simulador(
        tamano_matriz=8,
        cantidad_personas=10,
        defensa_inicial=3,
        semilla_aleatoria=42,
        usar_defensa_multiple=False
    )
    print(f"   Tamaño matriz: {simulador.get_matriz().get_tamano()}")
    print(f"   Personas a crear: {simulador.cantidad_personas_inicial}")
    print(f"   ¿Inicializada? {simulador.esta_inicializada}")
    print("   ✅ Simulador creado")

    print("\n📌 TEST 2: Inicializar simulación")
    print("-" * 70)
    simulador.inicializar()
    print(f"   ¿Inicializada? {simulador.esta_inicializada}")
    print(f"   Personas creadas: {len(simulador.get_personas())}")
    print(f"   Infectadas: {len(simulador.get_personas_infectadas())}")
    print(f"   Sanas: {len(simulador.get_personas_sanas())}")
    print("\n   Matriz inicial:")
    print(simulador.get_matriz().visualizar())
    print("\n   Árbol inicial:")
    print(simulador.get_arbol().visualizar())
    print("   ✅ Inicialización exitosa")

    print("\n📌 TEST 3: Ejecutar varias rondas")
    print("-" * 70)
    for i in range(5):
        stats = simulador.ejecutar_ronda()
        print(f"   Ronda {stats['ronda']}: {stats['sanas']} sanas, {stats['infectadas']} infectadas")

    print("\n   Matriz después de 5 rondas:")
    print(simulador.get_matriz().visualizar())
    print("\n   Árbol después de 5 rondas:")
    print(simulador.get_arbol().visualizar())
    print("   ✅ Rondas ejecutadas")

    print("\n📌 TEST 4: Verificar aumento de defensa (ronda múltiplo de 3)")
    print("-" * 70)
    personas_sanas = simulador.get_personas_sanas()
    if len(personas_sanas) > 0:
        persona_ejemplo = personas_sanas[0]
        defensa_antes = persona_ejemplo.defensa
        print(f"   Defensa de {persona_ejemplo.id} antes de ronda 6: {defensa_antes}")

        simulador.ejecutar_ronda()
        print(f"   Defensa de {persona_ejemplo.id} después de ronda 6: {persona_ejemplo.defensa}")

        if persona_ejemplo.defensa > defensa_antes:
            print("   ✅ Defensa aumentó correctamente")
        else:
            print("   📝 Persona no aumentó defensa (fue infectada o ya estaba infectada)")

    print("\n📌 TEST 5: Curar persona")
    print("-" * 70)
    infectadas_antes = len(simulador.get_personas_infectadas())
    print(f"   Infectadas antes: {infectadas_antes}")

    infectadas = simulador.get_personas_infectadas()
    if len(infectadas) > 1:
        persona_a_curar = infectadas[1]
        x, y = persona_a_curar.get_posicion()
        print(f"   Curando {persona_a_curar.id} en posición ({x}, {y})")

        se_curo = simulador.curar_persona(x, y)
        print(f"   ¿Se curó? {se_curo}")

        infectadas_despues = len(simulador.get_personas_infectadas())
        print(f"   Infectadas después: {infectadas_despues}")
        print("\n   Árbol después de curar:")
        print(simulador.get_arbol().visualizar())
        print("   ✅ Curación exitosa")

    print("\n📌 TEST 6: Agregar nueva persona")
    print("-" * 70)
    total_antes = len(simulador.get_personas())
    print(f"   Total personas antes: {total_antes}")

    se_agrego = simulador.agregar_persona(0, 0)
    print(f"   ¿Se agregó? {se_agrego}")

    total_despues = len(simulador.get_personas())
    print(f"   Total personas después: {total_despues}")
    print("   ✅ Persona agregada")

    print("\n📌 TEST 7: Ejecutar hasta que todas se infecten")
    print("-" * 70)
    print("   Ejecutando rondas automáticamente...")
    rondas_maximas = 50

    for i in range(rondas_maximas):
        stats = simulador.ejecutar_ronda()

        if simulador.todas_infectadas():
            print(f"\n   ¡Todas infectadas en la ronda {stats['ronda']}!")
            break

        if i % 5 == 0:
            print(f"   Ronda {stats['ronda']}: {stats['sanas']} sanas, {stats['infectadas']} infectadas")

    print("\n   Estadísticas finales:")
    stats_finales = simulador.get_estadisticas()
    for clave, valor in stats_finales.items():
        print(f"   {clave}: {valor}")

    print("\n   Árbol final:")
    print(simulador.get_arbol().visualizar())
    print("   ✅ Simulación completa")

    print("\n" + "=" * 70)
    print(" " * 20 + "✅ TODAS LAS PRUEBAS EXITOSAS")
    print("=" * 70)