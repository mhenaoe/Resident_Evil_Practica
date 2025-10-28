# Descripción del Proyecto.
Resident Evil es una simulación que modela la propagación de una infección dentro de una matriz NxN donde se ubican varias personas que se mueven aleatoriamente en cada ronda. 
Una de ellas es elegida aleatoriamente como el paciente cero, mientras las demás comienzan sanas con un nivel de defensa inicial. Durante la simulación, cuando una persona infectada 
comparte celda con una persona sana, esta última pierde puntos de defensa. 
Si su defensa llega a cero, se infecta automáticamente y el sistema actualiza el árbol de propagación, registrando quién contagió a quién.

### El programa permite:

 1. Simular movimientos aleatorios en 8 direcciones (norte, sur, este, oeste y diagonales).
 2. Visualizar la matriz con personas sanas e infectadas.
 3. Mostrar el árbol de contagio actualizado después de cada ronda.
 4. Curar personas mediante coordenadas específicas, modificando el árbol de propagación.
 5. Agregar nuevas personas sanas durante la simulación.
 6. Aumentar la defensa de las personas sanas cada tres rondas.
 7. Finalizar la simulación cuando todas las personas estén infectadas o el usuario lo decida.
 8. Esta práctica integra conceptos de programación orientada a objetos, aleatoriedad controlada, estructuras de datos dinámicas y visualización en consola, permitiendo analizar la evolución de una infección de forma clara e interactiva.


### Estructura de las clases: 

Clase Persona
Representa a cada individuo en la simulación.Contiene su posición, nivel de defensa y estado de infección.Permite moverse por la matriz, infectarse, curarse y modificar su defensa.
Clase NodoArbol
Modela un nodo dentro del árbol de contagio.Cada nodo guarda una persona, su padre (quién la infectó) y sus hijos (a quiénes infectó).
Clase ArbolContagio
Administra el árbol de propagación de la infección. Registra las relaciones de contagio, permite visualizar el árbol y eliminar nodos al curar personas.
Clase Matriz
Representa el entorno NxN donde se ubican las personas. Permite moverlas, agregarlas y visualizar su distribución.
Clase Simulador
Es el núcleo del programa. Controla las rondas, los movimientos, contagios, curaciones y estadísticas. Se apoya en las clases Matriz, ArbolContagio y Persona.
Clase Visualizador
Maneja la visualización en consola del estado del sistema. Permite mostrar la matriz, el árbol de contagio, estadísticas y defensas.
 Clase Main
Controla el flujo principal del programa. Muestra el menú, gestiona el modo de ejecución y lanza la simulación.




