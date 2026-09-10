"""
============================================================================
 ANALIZADOR CPM (Critical Path Method) - Red de Proyectos
============================================================================
Programa que, a partir de la descripción de un proyecto (actividades,
predecesoras y duraciones), calcula:

  1. La RED del proyecto (relaciones de precedencia / grafo dirigido)
  2. La RUTA CRÍTICA (paso adelantado + paso retrasado + condición triple
     de actividad crítica, según el algoritmo de Taha, sección 6.5.2)
  3. Los FLOTANTES total y libre de cada actividad (sección 6.5.2-6.5.3)
  4. El CRONOGRAMA del proyecto (diagrama de Gantt) con actividades
     críticas resaltadas

Modelo usado: Actividad-en-el-Nodo (AON / Precedence Diagram Method), que
es matemáticamente equivalente al modelo Actividad-en-el-Arco (AOA) del
libro, pero no requiere actividades ficticias porque las precedencias se
declaran directamente entre actividades en lugar de entre nodos-evento.

Autor: Analizador CPM educativo — basado en Taha, "Investigación de
Operaciones", 9na ed., Capítulo 6.
============================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


# ============================================================================
# 1. ESTRUCTURA DE DATOS DE ENTRADA
# ============================================================================

@dataclass
class Activity:
    """Representa una actividad del proyecto."""
    id: str                      # identificador corto (A, B, C, ...)
    name: str                    # descripción legible
    duration: float              # Dij : duración de la actividad
    predecessors: List[str] = field(default_factory=list)

    # --- resultados que se calculan durante el análisis CPM ---
    es: float = 0.0   # Early Start   (tiempo de inicio más temprano)
    ef: float = 0.0   # Early Finish  (tiempo de terminación más temprano)
    ls: float = 0.0   # Late Start    (tiempo de inicio más tardío)
    lf: float = 0.0   # Late Finish   (tiempo de terminación más tardío)
    tf: float = 0.0   # Total Float   (flotante total,  TFij = LSij - ESij)
    ff: float = 0.0   # Free Float    (flotante libre,  FFij = min(ES suc) - EFij)
    is_critical: bool = False


# ============================================================================
# 2. MOTOR DE CÁLCULO CPM
# ============================================================================

class CPMNetwork:
    """
    Implementa el algoritmo de la Ruta Crítica (CPM) descrito en la
    sección 6.5.2 del libro:

        Paso adelantado:  nj = max{ ni + Dij }  sobre arcos entrantes
        Paso retrasado:   Δj = min{ Δk - Djk }  sobre arcos salientes
        Actividad crítica (i,j) si:
            (1) Δi = ni
            (2) Δj = nj
            (3) Δj - ni = Dij
        Flotante total:  TFij = Δj - ni - Dij
        Flotante libre:  FFij = nj - ni - Dij   (FFij <= TFij siempre)
    """

    def __init__(self, activities: Dict[str, Activity]):
        self.activities = activities
        self._validar_proyecto()
        self.duracion_proyecto: float = 0.0
        self.ruta_critica: List[str] = []

    # ------------------------------------------------------------------
    def _validar_proyecto(self):
        """Verifica integridad de datos y ausencia de ciclos (regla 3 de
        Taha: la red no puede contener bucles / precedencias circulares)."""
        ids = set(self.activities.keys())
        for act in self.activities.values():
            for pred in act.predecessors:
                if pred not in ids:
                    raise ValueError(
                        f"La actividad '{act.id}' referencia una "
                        f"predecesora inexistente: '{pred}'"
                    )
        if self._tiene_ciclo():
            raise ValueError(
                "La red contiene un ciclo de precedencias (bucle). "
                "Un proyecto CPM debe ser una red acíclica dirigida (DAG)."
            )

    def _tiene_ciclo(self) -> bool:
        visitado, en_pila = set(), set()

        def dfs(nodo):
            visitado.add(nodo)
            en_pila.add(nodo)
            for pred in self.activities[nodo].predecessors:
                if pred not in visitado:
                    if dfs(pred):
                        return True
                elif pred in en_pila:
                    return True
            en_pila.remove(nodo)
            return False

        return any(dfs(n) for n in self.activities if n not in visitado)

    # ------------------------------------------------------------------
    def _sucesores(self, act_id: str) -> List[str]:
        """Devuelve la lista de actividades que tienen a act_id como
        predecesora directa (arcos salientes en la red)."""
        return [a.id for a in self.activities.values()
                if act_id in a.predecessors]

    def _orden_topologico(self) -> List[str]:
        """Orden topológico necesario para recorrer la red respetando
        las precedencias (requerido tanto en el paso adelantado como en
        el paso retrasado)."""
        visitado, orden = set(), []

        def dfs(nodo):
            visitado.add(nodo)
            for pred in self.activities[nodo].predecessors:
                if pred not in visitado:
                    dfs(pred)
            orden.append(nodo)

        for n in self.activities:
            if n not in visitado:
                dfs(n)
        return orden

    # ------------------------------------------------------------------
    def calcular(self):
        """Ejecuta el paso adelantado, el paso retrasado, calcula
        flotantes y determina la ruta crítica."""
        orden = self._orden_topologico()

        # ---------- PASO ADELANTADO (Early Start / Early Finish) --------
        for act_id in orden:
            act = self.activities[act_id]
            if not act.predecessors:
                act.es = 0.0
            else:
                act.es = max(self.activities[p].ef for p in act.predecessors)
            act.ef = act.es + act.duration

        # Duración total del proyecto = máxima EF entre actividades
        # terminales (sin sucesoras) -> equivale a nn en la notación de Taha
        terminales = [a for a in self.activities.values()
                      if not self._sucesores(a.id)]
        self.duracion_proyecto = max(a.ef for a in terminales)

        # ---------- PASO RETRASADO (Late Start / Late Finish) -----------
        for act_id in reversed(orden):
            act = self.activities[act_id]
            sucesores = self._sucesores(act_id)
            if not sucesores:
                act.lf = self.duracion_proyecto
            else:
                act.lf = min(self.activities[s].ls for s in sucesores)
            act.ls = act.lf - act.duration

        # ---------- FLOTANTES Y CONDICIÓN DE ACTIVIDAD CRÍTICA -----------
        for act in self.activities.values():
            act.tf = act.ls - act.es                       # = Δj - ni - Dij
            sucesores = self._sucesores(act.id)
            if sucesores:
                act.ff = min(self.activities[s].es for s in sucesores) - act.ef
            else:
                act.ff = self.duracion_proyecto - act.ef
            # Las 3 condiciones de Taha colapsan, en notación AON, a TF == 0
            act.is_critical = abs(act.tf) < 1e-9

        self.ruta_critica = [a.id for a in self.activities.values()
                              if a.is_critical]
        return self

    # ------------------------------------------------------------------
    # 3. REPORTES DE TEXTO
    # ------------------------------------------------------------------
    def imprimir_red(self):
        print("\n" + "=" * 78)
        print(" 1. RED DEL PROYECTO (relaciones de precedencia)")
        print("=" * 78)
        print(f"{'Actividad':<10}{'Descripción':<32}{'Duración':<10}{'Predecesoras'}")
        print("-" * 78)
        for a in self.activities.values():
            preds = ", ".join(a.predecessors) if a.predecessors else "— (inicio)"
            print(f"{a.id:<10}{a.name:<32}{a.duration:<10}{preds}")

    def imprimir_calculos_cpm(self):
        print("\n" + "=" * 78)
        print(" 2. CÁLCULOS DE LA RUTA CRÍTICA (paso adelantado / paso retrasado)")
        print("=" * 78)
        hdr = f"{'Act.':<6}{'Dur.':>6}{'ES':>7}{'EF':>7}{'LS':>7}{'LF':>7}{'TF':>7}{'FF':>7}  Crítica"
        print(hdr)
        print("-" * len(hdr))
        for a in self.activities.values():
            marca = "  *** SI ***" if a.is_critical else ""
            print(f"{a.id:<6}{a.duration:>6.1f}{a.es:>7.1f}{a.ef:>7.1f}"
                  f"{a.ls:>7.1f}{a.lf:>7.1f}{a.tf:>7.1f}{a.ff:>7.1f}{marca}")

    def imprimir_resumen(self):
        print("\n" + "=" * 78)
        print(" 3. RESUMEN")
        print("=" * 78)
        print(f"Duración total del proyecto : {self.duracion_proyecto:.1f} unidades de tiempo")
        print(f"Ruta crítica                 : "
              f"{' -> '.join(self._ordenar_ruta_critica())}")
        print("\nRegla de la señal roja (Taha, 6.5.3): una actividad no "
              "crítica con FF < TF puede\n"
              "demorarse como máximo FF sin afectar a sus sucesoras; "
              "demoras entre FF y TF\nretrasan el inicio de las "
              "actividades siguientes en (demora - FF).")
        con_bandera = [a for a in self.activities.values()
                       if not a.is_critical and a.ff < a.tf - 1e-9]
        if con_bandera:
            print("\nActividades con 'señal roja' (FF < TF):")
            for a in con_bandera:
                print(f"  - {a.id}: TF={a.tf:.1f}, FF={a.ff:.1f}  "
                      f"(demora máx. segura = {a.ff:.1f})")
        else:
            print("\nNinguna actividad no crítica presenta señal roja "
                  "(FF = TF en todas ellas).")

    def _ordenar_ruta_critica(self) -> List[str]:
        """Ordena las actividades críticas en secuencia de ejecución
        (por su tiempo de inicio más temprano)."""
        criticas = [self.activities[a] for a in self.ruta_critica]
        criticas.sort(key=lambda a: a.es)
        return [a.id for a in criticas]

    # ------------------------------------------------------------------
    # 4. DIAGRAMA DE RED (grafo dirigido, ruta crítica resaltada)
    # ------------------------------------------------------------------
    def graficar_red(self, ruta_salida: str):
        G = nx.DiGraph()
        for a in self.activities.values():
            etiqueta = f"{a.id}\n{a.duration:g}"
            G.add_node(a.id, label=etiqueta)
            for pred in a.predecessors:
                G.add_edge(pred, a.id)

        pos = nx.nx_agraph.graphviz_layout(G, prog="dot") \
            if _tiene_graphviz() else _layout_por_niveles(self, G)

        n_niveles = len(set(round(x, 3) for x, _ in pos.values()))
        n_max_por_nivel = max(
            sum(1 for _, y in pos.values() if True) // max(n_niveles, 1), 1
        )
        # Tamaño de figura acotado: crece con la cantidad de niveles/nodos
        # pero nunca de forma descontrolada (evita imágenes gigantes en
        # proyectos con muchas actividades).
        ancho = min(28, max(11, 1.1 * n_niveles))
        alto = min(16, max(6, 0.9 * n_max_por_nivel + 4))
        fig, ax = plt.subplots(figsize=(ancho, alto))

        colores_nodo = ["#E24B4A" if self.activities[n].is_critical
                        else "#85B7EB" for n in G.nodes()]

        # Arcos consecutivos en la ruta crítica se pintan en rojo/grueso
        ruta_ordenada = self._ordenar_ruta_critica()
        arcos_criticos = set(zip(ruta_ordenada, ruta_ordenada[1:]))

        # Cada arco se dibuja por separado con curvatura proporcional a la
        # distancia horizontal entre nodos, para que los arcos "largos" se
        # arqueen por encima/debajo y no atraviesen nodos intermedios.
        for u, v in G.edges():
            es_critico = (u, v) in arcos_criticos
            dx = abs(pos[v][0] - pos[u][0])
            salto_niveles = round(dx / max(dx, 1e-9))  # normaliza a 1 unidad
            niveles_de_por_medio = sum(
                1 for n in G.nodes()
                if min(pos[u][0], pos[v][0]) < pos[n][0] < max(pos[u][0], pos[v][0])
            )
            rad = 0.0 if niveles_de_por_medio == 0 else 0.25 + 0.08 * niveles_de_por_medio
            if pos[u][1] > pos[v][1]:
                rad = -rad
            nx.draw_networkx_edges(
                G, pos, edgelist=[(u, v)], ax=ax,
                edge_color="#E24B4A" if es_critico else "#9c9a92",
                width=2.6 if es_critico else 1.1,
                arrowsize=16,
                connectionstyle=f"arc3,rad={rad}",
            )

        nx.draw_networkx_nodes(G, pos, node_color=colores_nodo,
                                node_size=1700, edgecolors="black",
                                linewidths=0.8, ax=ax)
        etiquetas = {n: G.nodes[n]["label"] for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=etiquetas, font_size=9,
                                 font_weight="bold", ax=ax)

        parche_critico = mpatches.Patch(color="#E24B4A", label="Actividad crítica")
        parche_normal = mpatches.Patch(color="#85B7EB", label="Actividad no crítica")
        ax.set_title("Red del proyecto — Ruta crítica resaltada en rojo")
        ax.legend(handles=[parche_critico, parche_normal],
                  loc="upper center", bbox_to_anchor=(0.5, -0.05),
                  ncol=2, frameon=False)

        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        ax.set_xlim(min(xs) - 1, max(xs) + 1)
        ax.set_ylim(min(ys) - 1.2, max(ys) + 1.2)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(ruta_salida, dpi=150)
        plt.close()
        print(f"\n[Guardado] Diagrama de red: {ruta_salida}")

    # ------------------------------------------------------------------
    # 5. CRONOGRAMA (DIAGRAMA DE GANTT)
    # ------------------------------------------------------------------
    def graficar_gantt(self, ruta_salida: str):
        actividades = sorted(self.activities.values(), key=lambda a: a.es)
        fig, ax = plt.subplots(figsize=(11, 0.55 * len(actividades) + 2))

        for i, a in enumerate(actividades):
            y = len(actividades) - i - 1
            if a.is_critical:
                # Actividad crítica: sin holgura, una sola barra roja
                ax.barh(y, a.duration, left=a.es, height=0.5,
                        color="#E24B4A", edgecolor="black")
            else:
                # Actividad no crítica: barra de duración (azul) +
                # barra de holgura total (gris claro) hasta LF
                ax.barh(y, a.duration, left=a.es, height=0.5,
                        color="#378ADD", edgecolor="black")
                holgura = a.lf - a.ef
                if holgura > 1e-9:
                    ax.barh(y, holgura, left=a.ef, height=0.5,
                            color="#D3D1C7", edgecolor="black",
                            hatch="//", alpha=0.6)
            ax.text(a.es - 0.15, y, a.id, va="center", ha="right",
                    fontsize=9, fontweight="bold")

        ax.axvline(self.duracion_proyecto, color="black", linestyle="--",
                   linewidth=1)
        ax.text(self.duracion_proyecto, len(actividades) + 0.3,
                f" Fin del proyecto = {self.duracion_proyecto:g}",
                fontsize=9, ha="left")

        ax.set_yticks([])
        ax.set_xlabel("Tiempo (unidades)")
        ax.set_title("Cronograma del proyecto (diagrama de Gantt)\n"
                     "Rojo = actividad crítica  |  Azul = actividad no crítica  |  "
                     "Rayado = holgura total")
        ax.set_xlim(left=-max(1, self.duracion_proyecto * 0.02))
        ax.grid(axis="x", linestyle=":", alpha=0.5)
        plt.tight_layout()
        plt.savefig(ruta_salida, dpi=150)
        plt.close()
        print(f"[Guardado] Diagrama de Gantt: {ruta_salida}")


# ============================================================================
# UTILIDADES DE DISTRIBUCIÓN (fallback de layout cuando no hay graphviz)
# ============================================================================

def _tiene_graphviz() -> bool:
    try:
        import pygraphviz  # noqa: F401
        return True
    except ImportError:
        return False


def _layout_por_niveles(cpm: "CPMNetwork", G: nx.DiGraph) -> dict:
    """Ubica los nodos por 'nivel' (= ES redondeado) en el eje X y los
    distribuye verticalmente para evitar solapamientos, sin depender de
    graphviz (que no siempre está disponible)."""
    niveles: Dict[float, List[str]] = {}
    for a in cpm.activities.values():
        niveles.setdefault(a.es, []).append(a.id)

    # Normaliza los niveles (valores de ES) a posiciones enteras
    # equiespaciadas en X, y separa verticalmente los nodos de cada nivel.
    valores_ordenados = sorted(niveles.keys())
    escala_x = {v: i * 3.0 for i, v in enumerate(valores_ordenados)}

    pos = {}
    for x_original, nodos in niveles.items():
        nodos = sorted(nodos)
        n = len(nodos)
        x = escala_x[x_original]
        for i, nodo in enumerate(nodos):
            y = (i - (n - 1) / 2) * 2.6
            pos[nodo] = (x, y)
    return pos


# ============================================================================
# 6. FUNCIÓN DE CONVENIENCIA: DESCRIPCIÓN DE PROYECTO -> ANÁLISIS COMPLETO
# ============================================================================

def analizar_proyecto(descripcion: List[dict],
                       carpeta_salida: str = "salidas",
                       prefijo: str = "proyecto") -> CPMNetwork:
    """
    Punto de entrada principal. Recibe la DESCRIPCIÓN DEL PROYECTO como
    una lista de diccionarios con el formato:

        {"id": "A", "nombre": "Excavar cimientos",
         "duracion": 3, "predecesoras": []}

    y ejecuta el análisis CPM completo: red, ruta crítica y cronograma.
    """
    os.makedirs(carpeta_salida, exist_ok=True)

    actividades = {
        d["id"]: Activity(id=d["id"], name=d.get("nombre", d["id"]),
                           duration=d["duracion"],
                           predecessors=d.get("predecesoras", []))
        for d in descripcion
    }

    red = CPMNetwork(actividades).calcular()

    red.imprimir_red()
    red.imprimir_calculos_cpm()
    red.imprimir_resumen()

    red.graficar_red(os.path.join(carpeta_salida, f"{prefijo}_red.png"))
    red.graficar_gantt(os.path.join(carpeta_salida, f"{prefijo}_gantt.png"))

    return red


# ============================================================================
# 7. EJEMPLO DE USO — Proyecto del libro de Taha (Ejemplo 6.5-2)
# ============================================================================
if __name__ == "__main__":

    # -----------------------------------------------------------------
    # DESCRIPCIÓN DEL PROYECTO
    # (equivalente en AON al ejemplo 6.5-2 / 6.5-5 de Taha; la actividad
    #  ficticia del libro se traduce aquí como precedencia directa)
    # -----------------------------------------------------------------
    proyecto_taha = [
        {"id": "A", "nombre": "Actividad A", "duracion": 5,  "predecesoras": []},
        {"id": "B", "nombre": "Actividad B", "duracion": 6,  "predecesoras": []},
        {"id": "C", "nombre": "Actividad C", "duracion": 3,  "predecesoras": ["A"]},
        {"id": "D", "nombre": "Actividad D", "duracion": 8,  "predecesoras": ["A"]},
        {"id": "E", "nombre": "Actividad E", "duracion": 2,  "predecesoras": ["B", "C"]},
        {"id": "F", "nombre": "Actividad F", "duracion": 11, "predecesoras": ["B", "C"]},
        {"id": "G", "nombre": "Actividad G", "duracion": 1,  "predecesoras": ["D"]},
        {"id": "H", "nombre": "Actividad H", "duracion": 12, "predecesoras": ["D", "E"]},
    ]

    print("#" * 78)
    print("# VALIDACIÓN CON EL EJEMPLO 6.5-2 DE TAHA")
    print("# Resultado esperado del libro: duración = 25, ruta crítica A-D-H")
    print("#" * 78)
    analizar_proyecto(proyecto_taha, carpeta_salida="salidas",
                       prefijo="validacion_taha")
