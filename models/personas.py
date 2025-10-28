
from typing import Optional, Any

class Persona:
    def __init__(self, id: str, x:int, y:int, defensa_inicial: int = 3):
        
        self.id: str = id
        self.x: int = x
        self.y: int = y
        self.infectada: bool = False
        self.defensa: int = defensa_inicial
        self.infectador: Optional['Persona'] = None
        self.infectador: Opcional[ 'Persona'] = None
        
    def get_posicion(self) -> tuple[int, int]:
        ...
    
    def set_posicion(self, x: int, y:int) -> None:
        ...
        
    def esta_infectada(self) -> bool:
        ...
        
    def reducir_defensa(self) -> None:
        ...
        
    def aumentar_defensa(self) -> None:
        ...
        
    def infectar(self, infectador: Persona) -> None:
        ...
        
    def curar(self) -> None:
        ...
        
    def __repr__(self) -> str:
        ...
        
    def __eq__(self, other: object) -> bool:
        ...
        
    
        
        
 

