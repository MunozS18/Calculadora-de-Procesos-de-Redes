"""
Ejemplo de USO del analizador CPM con un proyecto propio.

Este archivo NO modifica cpm_analyzer.py: solo importa la función
analizar_proyecto() y le pasa una descripción de proyecto distinta,
demostrando que el programa es de propósito general.

Proyecto: construcción de una casa nueva
(datos tomados del problema 6, conjunto de problemas 6.5a, Taha 9na ed.)
"""

from cpm_analyzer import analizar_proyecto

proyecto_casa = [
    {"id": "A", "nombre": "Limpiar el terreno",              "duracion": 1,  "predecesoras": []},
    {"id": "B", "nombre": "Llevar servicios al terreno",      "duracion": 2,  "predecesoras": []},
    {"id": "C", "nombre": "Excavar",                          "duracion": 1,  "predecesoras": ["A"]},
    {"id": "D", "nombre": "Colar los cimientos",              "duracion": 2,  "predecesoras": ["C"]},
    {"id": "E", "nombre": "Plomería externa",                 "duracion": 6,  "predecesoras": ["B", "C"]},
    {"id": "F", "nombre": "Armar estructura de la casa",      "duracion": 10, "predecesoras": ["D"]},
    {"id": "G", "nombre": "Instalar cableado eléctrico",      "duracion": 3,  "predecesoras": ["F"]},
    {"id": "H", "nombre": "Colocar el piso",                  "duracion": 1,  "predecesoras": ["G"]},
    {"id": "I", "nombre": "Colocar el techo",                 "duracion": 1,  "predecesoras": ["F"]},
    {"id": "J", "nombre": "Plomería interior",                "duracion": 5,  "predecesoras": ["E", "H"]},
    {"id": "K", "nombre": "Colocar tejas",                    "duracion": 2,  "predecesoras": ["I"]},
    {"id": "L", "nombre": "Recubrimiento aislante exterior",  "duracion": 1,  "predecesoras": ["F", "J"]},
    {"id": "M", "nombre": "Instalar ventanas y puertas ext.", "duracion": 2,  "predecesoras": ["F"]},
    {"id": "N", "nombre": "Enladrillar",                      "duracion": 4,  "predecesoras": ["L", "M"]},
    {"id": "O", "nombre": "Aislar muros y cielo raso",        "duracion": 2,  "predecesoras": ["G", "J"]},
    {"id": "P", "nombre": "Cubrir muros y cielo raso",        "duracion": 2,  "predecesoras": ["O"]},
    {"id": "Q", "nombre": "Aislar techo",                     "duracion": 1,  "predecesoras": ["I", "P"]},
    {"id": "R", "nombre": "Terminar interiores",              "duracion": 7,  "predecesoras": ["P"]},
    {"id": "S", "nombre": "Terminar exteriores",               "duracion": 7,  "predecesoras": ["I", "N"]},
    {"id": "T", "nombre": "Jardinería",                        "duracion": 3,  "predecesoras": ["S"]},
]

if __name__ == "__main__":
    print("#" * 78)
    print("# EJEMPLO 2: PROYECTO DE CONSTRUCCIÓN DE UNA CASA")
    print("# (Problema 6, conjunto 6.5a — Taha 9na ed.)")
    print("#" * 78)
    analizar_proyecto(proyecto_casa,
                       carpeta_salida="salidas",
                       prefijo="ejemplo_casa")
