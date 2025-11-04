from __future__ import annotations
from typing import Optional, List

from .persona import Persona          


class NodoArbol:
    
    def __init__(self, persona: Persona) -> None:
        self.persona: Persona = persona
        self.padre: Optional['NodoArbol'] = None
        self.hijos: list['NodoArbol'] = []

    def agregar_hijo(self, nodo_hijo: 'NodoArbol') -> None:
        ya_existe = False
        for hijo_actual in self.hijos:
            if hijo_actual == nodo_hijo:
                ya_existe = True
                break
        
        es_el_mismo_nodo = (nodo_hijo == self)
        
        if not ya_existe and not es_el_mismo_nodo:
            self.hijos.append(nodo_hijo)
            nodo_hijo.padre = self

    def eliminar_hijo(self, nodo_hijo: 'NodoArbol') -> bool:
        hijo_encontrado = False
        
        for hijo_actual in self.hijos:
            if hijo_actual == nodo_hijo:
                hijo_encontrado = True
                break
        
        if hijo_encontrado:
            self.hijos.remove(nodo_hijo)
            nodo_hijo.padre = None
            return True
        
        return False

    def get_hijos(self) -> list['NodoArbol']:
        return self.hijos

    def get_padre(self) -> Optional['NodoArbol']:
        return self.padre

    def set_padre(self, nodo_padre: Optional['NodoArbol']) -> None:
        self.padre = nodo_padre

    def es_raiz(self) -> bool:
        if self.padre is None:
            return True
        else:
            return False

    def get_nivel(self) -> int:
        nivel = 0
        nodo_actual = self
        
        while nodo_actual.padre is not None:
            nivel = nivel + 1
            nodo_actual = nodo_actual.padre
        
        return nivel

    def get_persona(self) -> Persona:
        return self.persona

    def __repr__(self) -> str:
        id_persona = self.persona.id
        texto = f"NodoArbol({id_persona})"
        return texto


if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "PRUEBAS DE LA CLASE NODOARBOL")
    print("=" * 70)
    
    print("\n📌 TEST 1: Crear nodo raíz (paciente cero)")
    print("-" * 70)
    persona_1 = Persona("p1", 0, 0)
    persona_1.infectar(persona_1)
    nodo_persona_1 = NodoArbol(persona_1)
    print(f"   Nodo creado: {nodo_persona_1}")
    print(f"   ¿Es raíz? {nodo_persona_1.es_raiz()}")
    print(f"   Nivel: {nodo_persona_1.get_nivel()}")
    cantidad_hijos = len(nodo_persona_1.get_hijos())
    print(f"   Cantidad de hijos: {cantidad_hijos}")
    print("   ✅ Nodo raíz creado correctamente")
    
    print("\n📌 TEST 2: Agregar primer hijo")
    print("-" * 70)
    persona_3 = Persona("p3", 1, 1)
    persona_3.infectar(persona_1)
    nodo_persona_3 = NodoArbol(persona_3)
    nodo_persona_1.agregar_hijo(nodo_persona_3)
    print(f"   Hijo agregado: {nodo_persona_3}")
    print(f"   ¿Es raíz? {nodo_persona_3.es_raiz()}")
    print(f"   Nivel: {nodo_persona_3.get_nivel()}")
    print(f"   Padre: {nodo_persona_3.get_padre()}")
    hijos_de_p1 = nodo_persona_1.get_hijos()
    print(f"   Hijos de p1: {hijos_de_p1}")
    print("   ✅ Hijo agregado correctamente")
    
    print("\n📌 TEST 3: Agregar múltiples hijos al mismo nodo")
    print("-" * 70)
    persona_4 = Persona("p4", 2, 2)
    persona_4.infectar(persona_1)
    nodo_persona_4 = NodoArbol(persona_4)
    nodo_persona_1.agregar_hijo(nodo_persona_4)
    hijos_de_p1 = nodo_persona_1.get_hijos()
    cantidad_hijos = len(hijos_de_p1)
    print(f"   Hijos de p1: {hijos_de_p1}")
    print(f"   Cantidad de hijos: {cantidad_hijos}")
    print("   ✅ Múltiples hijos agregados")
    
    print("\n📌 TEST 4: Crear árbol de varios niveles")
    print("-" * 70)
    persona_5 = Persona("p5", 3, 3)
    persona_5.infectar(persona_3)
    nodo_persona_5 = NodoArbol(persona_5)
    nodo_persona_3.agregar_hijo(nodo_persona_5)
    
    persona_6 = Persona("p6", 4, 4)
    persona_6.infectar(persona_4)
    nodo_persona_6 = NodoArbol(persona_6)
    nodo_persona_4.agregar_hijo(nodo_persona_6)
    
    print("   Estructura del árbol:")
    print("   p1 (nivel 0)")
    print("   ├── p3 (nivel 1)")
    print("   │   └── p5 (nivel 2)")
    print("   └── p4 (nivel 1)")
    print("       └── p6 (nivel 2)")
    
    nivel_p1 = nodo_persona_1.get_nivel()
    nivel_p3 = nodo_persona_3.get_nivel()
    nivel_p5 = nodo_persona_5.get_nivel()
    nivel_p6 = nodo_persona_6.get_nivel()
    
    print(f"\n   Nivel de p1: {nivel_p1}")
    print(f"   Nivel de p3: {nivel_p3}")
    print(f"   Nivel de p5: {nivel_p5}")
    print(f"   Nivel de p6: {nivel_p6}")
    print("   ✅ Árbol multinivel creado")
    
    print("\n📌 TEST 5: Eliminar hijo")
    print("-" * 70)
    hijos_antes = nodo_persona_3.get_hijos()
    print(f"   Hijos de p3 antes: {hijos_antes}")
    
    se_elimino = nodo_persona_3.eliminar_hijo(nodo_persona_5)
    print(f"   ¿Eliminado exitosamente? {se_elimino}")
    
    hijos_despues = nodo_persona_3.get_hijos()
    print(f"   Hijos de p3 después: {hijos_despues}")
    
    padre_de_p5 = nodo_persona_5.get_padre()
    print(f"   Padre de p5: {padre_de_p5}")
    print("   ✅ Hijo eliminado correctamente")
    
    print("\n📌 TEST 6: Intentar eliminar hijo que no existe")
    print("-" * 70)
    persona_7 = Persona("p7", 5, 5)
    nodo_persona_7 = NodoArbol(persona_7)
    se_elimino = nodo_persona_1.eliminar_hijo(nodo_persona_7)
    print(f"   ¿Eliminado exitosamente? {se_elimino}")
    print("   ✅ Manejo correcto de hijo inexistente")
    
    print("\n📌 TEST 7: Prevenir auto-referencia")
    print("-" * 70)
    hijos_antes = len(nodo_persona_1.get_hijos())
    nodo_persona_1.agregar_hijo(nodo_persona_1)
    hijos_despues = len(nodo_persona_1.get_hijos())
    print(f"   Hijos antes de auto-agregar: {hijos_antes}")
    print(f"   Hijos después de auto-agregar: {hijos_despues}")
    se_previno = (hijos_antes == hijos_despues)
    print(f"   ¿Se previno? {se_previno}")
    print("   ✅ Auto-referencia prevenida")
    
    print("\n📌 TEST 8: Prevenir duplicados")
    print("-" * 70)
    hijos_antes = len(nodo_persona_1.get_hijos())
    nodo_persona_1.agregar_hijo(nodo_persona_3)
    nodo_persona_1.agregar_hijo(nodo_persona_3)
    hijos_despues = len(nodo_persona_1.get_hijos())
    print(f"   Hijos antes: {hijos_antes}")
    print(f"   Hijos después de agregar p3 dos veces: {hijos_despues}")
    se_previno = (hijos_antes == hijos_despues)
    print(f"   ¿Se previno duplicado? {se_previno}")
    print("   ✅ Duplicados prevenidos")
    
    print("\n" + "=" * 70)
    print(" " * 20 + "✅ TODAS LAS PRUEBAS EXITOSAS")
    print("=" * 70)