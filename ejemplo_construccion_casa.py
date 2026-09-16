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
    {"id": "A", "nombre": "Revisión del trabajo", "duracion": "1", "predecesoras": []},
    {"id": "B", "nombre": "Avisar a los clientes del corte temporal de corriente", "duracion": "1/2", "predecesoras": ["A"]},
    {"id": "C", "nombre": "Tiendas de requisición", "duracion": "1", "predecesoras": ["A"]},
    {"id": "D", "nombre": "Explorar el trabajo", "duracion": "1/2", "predecesoras": ["A"]},
    {"id": "E", "nombre": "Asegurar los postes y materiales", "duracion": "3", "predecesoras": ["C", "D"]},
    {"id": "F", "nombre": "Distribuir los postes", "duracion": "3 1/2", "predecesoras": ["E"]},
    {"id": "G", "nombre": "Coordinar la ubicación de postes", "duracion": "1/2", "predecesoras": ["D"]},
    {"id": "H", "nombre": "Clavar estacas", "duracion": "1/2", "predecesoras": ["G"]},
    {"id": "I", "nombre": "Cavar agujeros", "duracion": "3", "predecesoras": ["H"]},
]

if __name__ == "__main__":
    print("#" * 78)
    print("# EJEMPLO 2: PROYECTO DE CONSTRUCCIÓN DE UNA CASA")
    print("# (Problema 6, conjunto 6.5a — Taha 9na ed.)")
    print("#" * 78)
    analizar_proyecto(proyecto_casa,
                       carpeta_salida="salidas",
                       prefijo="ejemplo_casa")
