import json
import os
import tkinter as tk
from fractions import Fraction
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from cpm_analyzer import Activity, CPMNetwork, format_duration, _to_fraction


def parse_duration(value):
    if value is None:
        raise ValueError("La duración no puede estar vacía.")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, (int, float)):
        return Fraction(str(value))
    texto = str(value).strip()
    if not texto or texto in {"-", "—"}:
        raise ValueError("La duración no puede estar vacía.")
    if " " in texto and "/" in texto:
        partes = texto.split()
        if len(partes) == 2:
            return parse_duration(partes[0]) + parse_duration(partes[1])
    return _to_fraction(texto.replace(" ", ""))


COLORS = {
    "bg": "#101419",
    "panel": "#171d24",
    "panel_alt": "#1e2630",
    "line": "#303b47",
    "text": "#edf2f7",
    "muted": "#9aa8b6",
    "accent": "#54d6c7",
    "accent_dark": "#183d3b",
    "critical": "#ff6b61",
    "blue": "#5aa9e6",
}


class CPMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPM Studio | Analizador de Procesos")
        self.geometry("1400x900")
        self.minsize(1100, 720)
        self.configure(bg=COLORS["bg"])
        self.activities = []
        self.network = None
        self.chart_canvases = {}
        self._configure_styles()
        self._build_ui()
        self._load_example()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Panel.TFrame", background=COLORS["panel"])
        style.configure("Card.TFrame", background=COLORS["panel_alt"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=COLORS["panel"], foreground=COLORS["muted"], font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI Semibold", 23))
        style.configure("Subtitle.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=("Segoe UI", 10))
        style.configure("CardValue.TLabel", background=COLORS["panel_alt"], foreground=COLORS["text"], font=("Segoe UI Semibold", 17))
        style.configure("CardCaption.TLabel", background=COLORS["panel_alt"], foreground=COLORS["muted"], font=("Segoe UI", 9))
        style.configure("Treeview", background=COLORS["panel_alt"], fieldbackground=COLORS["panel_alt"], foreground=COLORS["text"], rowheight=30, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=COLORS["line"], foreground=COLORS["text"], relief="flat", font=("Segoe UI Semibold", 9))
        style.map("Treeview", background=[("selected", "#24504e")], foreground=[("selected", "#ffffff")])
        style.configure("TNotebook", background=COLORS["panel"], borderwidth=0)
        style.configure("TNotebook.Tab", background=COLORS["panel_alt"], foreground=COLORS["muted"], padding=(18, 10), font=("Segoe UI Semibold", 10))
        style.map("TNotebook.Tab", background=[("selected", COLORS["accent_dark"])], foreground=[("selected", COLORS["accent"])])
        style.configure("TButton", background=COLORS["line"], foreground=COLORS["text"], padding=(12, 8), borderwidth=0, font=("Segoe UI Semibold", 9))
        style.map("TButton", background=[("active", "#435263")])
        style.configure("Accent.TButton", background=COLORS["accent"], foreground="#0a1717")
        style.map("Accent.TButton", background=[("active", "#7ce6dc")])
        style.configure("TEntry", fieldbackground=COLORS["panel_alt"], foreground=COLORS["text"], insertcolor=COLORS["text"], borderwidth=1)
        style.configure("TCombobox", fieldbackground=COLORS["panel_alt"], foreground=COLORS["text"])

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=28, pady=(24, 14))
        ttk.Label(header, text="CPM STUDIO", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Red de procesos  ·  Ruta crítica  ·  Cronograma inteligente", style="Subtitle.TLabel").pack(anchor="w", pady=(3, 0))

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=22, pady=(0, 20))
        body.columnconfigure(0, weight=0, minsize=370)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        self._build_editor(body)
        self._build_workspace(body)

    def _build_editor(self, parent):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        panel.rowconfigure(3, weight=1)
        ttk.Label(panel, text="Definición del proyecto", font=("Segoe UI Semibold", 14), background=COLORS["panel"], foreground=COLORS["text"]).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(panel, text="Agrega cada actividad y sus predecesoras directas.", style="Muted.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 16))

        form = ttk.Frame(panel, style="Panel.TFrame")
        form.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        form.columnconfigure(1, weight=1)
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.duration_var = tk.StringVar()
        self.predecessors_var = tk.StringVar()
        for row, label, var, width in [(0, "ID", self.id_var, 8), (1, "Actividad", self.name_var, 24), (2, "Duración", self.duration_var, 12), (3, "Predecesoras", self.predecessors_var, 24)]:
            ttk.Label(form, text=label, style="Muted.TLabel").grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=var, width=width).grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=4)
        self.predecessors_var.set("-")

        quick_frame = ttk.Frame(form, style="Panel.TFrame")
        quick_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Label(quick_frame, text="Fracciones rápidas", style="Muted.TLabel").pack(anchor="w")
        quick_values = ["1/2", "1", "3/2", "2", "3", "7/2", "3 1/2"]
        quick_bar = ttk.Frame(quick_frame, style="Panel.TFrame")
        quick_bar.pack(fill="x", pady=(6, 0))
        for value in quick_values:
            ttk.Button(quick_bar, text=value, command=lambda v=value: self._apply_duration_quick(v)).pack(side="left", padx=(0, 6), pady=2)

        ttk.Label(form, text="Soporta 1/2, 3/2, 3 1/2 y decimales.", style="Muted.TLabel").grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))

        buttons = ttk.Frame(form, style="Panel.TFrame")
        buttons.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(buttons, text="+ Agregar", style="Accent.TButton", command=self._add_activity).pack(side="left")
        ttk.Button(buttons, text="Actualizar", command=self._update_activity).pack(side="left", padx=7)
        ttk.Button(buttons, text="Limpiar", command=self._clear_form).pack(side="left")

        table_frame = ttk.Frame(panel, style="Panel.TFrame")
        table_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.activity_tree = ttk.Treeview(table_frame, columns=("id", "name", "duration", "pred"), show="headings", selectmode="browse")
        for col, text, width in [("id", "ID", 44), ("name", "Actividad", 150), ("duration", "Dur.", 52), ("pred", "Predecesoras", 105)]:
            self.activity_tree.heading(col, text=text)
            self.activity_tree.column(col, width=width, anchor="w")
        self.activity_tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.activity_tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.activity_tree.configure(yscrollcommand=scroll.set)
        self.activity_tree.bind("<<TreeviewSelect>>", self._select_activity)
        ttk.Button(panel, text="Eliminar seleccionada", command=self._delete_activity).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        bottom = ttk.Frame(panel, style="Panel.TFrame")
        bottom.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(bottom, text="Cargar ejemplo", command=self._load_example).pack(side="left")
        ttk.Button(bottom, text="Importar JSON", command=self._import_json).pack(side="left", padx=6)
        ttk.Button(bottom, text="Exportar JSON", command=self._export_json).pack(side="left")

    def _build_workspace(self, parent):
        workspace = ttk.Frame(parent)
        workspace.grid(row=0, column=1, sticky="nsew")
        workspace.rowconfigure(2, weight=1)
        workspace.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="Listo para analizar tu proyecto")
        toolbar = ttk.Frame(workspace)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        ttk.Button(toolbar, text="CALCULAR PROYECTO", style="Accent.TButton", command=self._calculate).pack(side="left")
        ttk.Label(toolbar, textvariable=self.status_var, style="Subtitle.TLabel").pack(side="left", padx=16)

        cards = ttk.Frame(workspace)
        cards.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        for index in range(4):
            cards.columnconfigure(index, weight=1)
        self.metric_vars = {}
        for index, (key, title) in enumerate([("duration", "DURACIÓN TOTAL"), ("critical", "ACTIVIDADES CRÍTICAS"), ("count", "ACTIVIDADES"), ("alerts", "SEÑALES ROJAS")]):
            card = ttk.Frame(cards, style="Card.TFrame", padding=(16, 12))
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 7, 7 if index < 3 else 0))
            self.metric_vars[key] = tk.StringVar(value="--")
            ttk.Label(card, textvariable=self.metric_vars[key], style="CardValue.TLabel").pack(anchor="w")
            ttk.Label(card, text=title, style="CardCaption.TLabel").pack(anchor="w", pady=(4, 0))

        self.notebook = ttk.Notebook(workspace)
        self.notebook.grid(row=2, column=0, sticky="nsew")
        self.results_tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=14)
        self.network_tab = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.gantt_tab = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.notebook.add(self.results_tab, text="  Resultados  ")
        self.notebook.add(self.network_tab, text="  Red del proceso  ")
        self.notebook.add(self.gantt_tab, text="  Cronograma  ")
        self._build_results()

    def _build_results(self):
        self.results_tab.rowconfigure(1, weight=1)
        self.results_tab.rowconfigure(2, weight=0)
        self.results_tab.columnconfigure(0, weight=1)
        self.critical_var = tk.StringVar(value="Calcula el proyecto para ver la ruta crítica")
        route = ttk.Frame(self.results_tab, style="Card.TFrame", padding=16)
        route.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(route, text="RUTA CRÍTICA", style="CardCaption.TLabel").pack(anchor="w")
        ttk.Label(route, textvariable=self.critical_var, background=COLORS["panel_alt"], foreground=COLORS["critical"], font=("Segoe UI Semibold", 15)).pack(anchor="w", pady=(6, 0))
        frame = ttk.Frame(self.results_tab, style="Panel.TFrame")
        frame.grid(row=1, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        cols = ("id", "name", "dur", "es", "ef", "ls", "lf", "tf", "ff", "critical")
        self.results_tree = ttk.Treeview(frame, columns=cols, show="headings")
        headings = {"id": "ID", "name": "Actividad", "dur": "Dur.", "es": "ES", "ef": "EF", "ls": "LS", "lf": "LF", "tf": "Flot. total", "ff": "Flot. libre", "critical": "Estado"}
        for col in cols:
            self.results_tree.heading(col, text=headings[col])
            self.results_tree.column(col, width=70 if col not in ("name", "critical") else (190 if col == "name" else 100), anchor="w")
        self.results_tree.tag_configure("critical", foreground=COLORS["critical"])
        self.results_tree.tag_configure("normal", foreground=COLORS["text"])
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.results_tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.results_tree.configure(yscrollcommand=scroll.set)
        self.results_tree.bind("<<TreeviewSelect>>", self._show_activity_detail)

        detail = ttk.Frame(self.results_tab, style="Card.TFrame", padding=14)
        detail.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        ttk.Label(detail, text="FICHA COMPLETA DE LA ACTIVIDAD", style="CardCaption.TLabel").pack(anchor="w")
        self.detail_var = tk.StringVar(value="Selecciona una actividad para ver todos sus parámetros calculados.")
        ttk.Label(detail, textvariable=self.detail_var, style="Muted.TLabel", justify="left", anchor="w").pack(fill="x", pady=(6, 0))
        ttk.Button(detail, text="Editar esta actividad en el formulario", command=self._edit_selected_result).pack(anchor="e", pady=(8, 0))

    def _load_example(self):
        self.activities = [
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
        self._refresh_activity_tree()
        self._clear_form()
        self._calculate()

    def _apply_duration_quick(self, value):
        self.duration_var.set(value)
        self.status_var.set(f"Duración rápida seleccionada: {value}")

    def _refresh_activity_tree(self):
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        for item in self.activities:
            pred = ", ".join(item["predecesoras"]) or "Inicio"
            self.activity_tree.insert("", "end", iid=item["id"], values=(item["id"], item["nombre"], format_duration(item["duracion"]), pred))

    def _clear_form(self):
        self.id_var.set("")
        self.name_var.set("")
        self.duration_var.set("")
        self.predecessors_var.set("-")
        for item in self.activity_tree.selection():
            self.activity_tree.selection_remove(item)

    def _parse_form(self):
        activity_id = self.id_var.get().strip().upper()
        name = self.name_var.get().strip()
        if not activity_id or not name:
            raise ValueError("El ID y el nombre de la actividad son obligatorios.")
        try:
            duration = parse_duration(self.duration_var.get())
        except (TypeError, ValueError):
            raise ValueError("La duración debe ser un número positivo, por ejemplo 3, 2.5 o 1/2.")
        if duration <= 0:
            raise ValueError("La duración debe ser mayor que cero.")
        pred_text = self.predecessors_var.get().replace("-", "").strip()
        predecessors = [p.strip().upper() for p in pred_text.split(",") if p.strip()]
        if activity_id in predecessors:
            raise ValueError("Una actividad no puede ser predecesora de sí misma.")
        return {"id": activity_id, "nombre": name, "duracion": duration, "predecesoras": predecessors}

    def _add_activity(self):
        try:
            activity = self._parse_form()
            if any(item["id"] == activity["id"] for item in self.activities):
                raise ValueError("Ya existe una actividad con ese ID.")
            self.activities.append(activity)
            self._refresh_activity_tree()
            self._clear_form()
            self._calculate()
        except ValueError as error:
            messagebox.showerror("Datos de actividad", str(error))

    def _update_activity(self):
        selected = self.activity_tree.selection()
        if not selected:
            messagebox.showinfo("Editar actividad", "Selecciona una actividad de la tabla.")
            return
        try:
            activity = self._parse_form()
            old_id = selected[0]
            if activity["id"] != old_id and any(item["id"] == activity["id"] for item in self.activities):
                raise ValueError("Ya existe una actividad con ese ID.")
            for item in self.activities:
                if item["id"] == old_id:
                    item.update(activity)
            for item in self.activities:
                item["predecesoras"] = [activity["id"] if pred == old_id else pred for pred in item["predecesoras"]]
            self._refresh_activity_tree()
            self._clear_form()
            self._calculate()
        except ValueError as error:
            messagebox.showerror("Datos de actividad", str(error))

    def _delete_activity(self):
        selected = self.activity_tree.selection()
        if not selected:
            return
        activity_id = selected[0]
        self.activities = [item for item in self.activities if item["id"] != activity_id]
        for item in self.activities:
            item["predecesoras"] = [pred for pred in item["predecesoras"] if pred != activity_id]
        self._refresh_activity_tree()
        self._clear_form()
        self._calculate()

    def _select_activity(self, _event=None):
        selected = self.activity_tree.selection()
        if not selected:
            return
        item = next((entry for entry in self.activities if entry["id"] == selected[0]), None)
        if item:
            self.id_var.set(item["id"])
            self.name_var.set(item["nombre"])
            self.duration_var.set(format_duration(item["duracion"]))
            self.predecessors_var.set(", ".join(item["predecesoras"]) or "-")

    def _calculate(self):
        if not self.activities:
            messagebox.showwarning("Proyecto vacío", "Agrega al menos una actividad.")
            return
        try:
            parsed = {
                item["id"]: Activity(item["id"], item["nombre"], parse_duration(item["duracion"]), item["predecesoras"])
                for item in self.activities
            }
            self.network = CPMNetwork(parsed).calcular()
            self._update_results()
            self._draw_charts()
            self.status_var.set("Análisis completado correctamente")
        except (ValueError, KeyError) as error:
            messagebox.showerror("No se puede calcular", str(error))
            self.status_var.set("Revisa las precedencias del proyecto")

    def _show_activity_detail(self, _event=None):
        selected = self.results_tree.selection()
        if not selected or not self.network:
            return
        activity = self.network.activities.get(selected[0])
        if not activity:
            return
        successors = [item.id for item in self.network.activities.values() if activity.id in item.predecessors]
        alert = (not activity.is_critical and activity.ff < activity.tf - 1e-9)
        self.detail_var.set(
            f"{activity.id} · {activity.name}\n"
            f"Duración: {format_duration(activity.duration)}    |    Predecesoras: {', '.join(activity.predecessors) or 'Inicio'}    |    "
            f"Sucesoras: {', '.join(successors) or 'Fin'}\n"
            f"Inicio temprano (ES): {format_duration(activity.es)}    |    Fin temprano (EF): {format_duration(activity.ef)}    |    "
            f"Inicio tardío (LS): {format_duration(activity.ls)}    |    Fin tardío (LF): {format_duration(activity.lf)}\n"
            f"Flotante total: {format_duration(activity.tf)}    |    Flotante libre: {format_duration(activity.ff)}    |    "
            f"Estado: {'CRÍTICA' if activity.is_critical else 'Normal'}    |    Señal roja: {'Sí' if alert else 'No'}"
        )
        if self.activity_tree.exists(activity.id):
            self.activity_tree.selection_set(activity.id)
            self.activity_tree.see(activity.id)

    def _edit_selected_result(self):
        selected = self.results_tree.selection()
        if selected and self.activity_tree.exists(selected[0]):
            self.activity_tree.selection_set(selected[0])
            self.activity_tree.see(selected[0])
            self._select_activity()

    def _update_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for activity in self.network.activities.values():
            values = (activity.id, activity.name, format_duration(activity.duration), format_duration(activity.es), format_duration(activity.ef), format_duration(activity.ls), format_duration(activity.lf), format_duration(activity.tf), format_duration(activity.ff), "CRÍTICA" if activity.is_critical else "Normal")
            self.results_tree.insert("", "end", iid=activity.id, values=values, tags=("critical" if activity.is_critical else "normal",))
        if self.results_tree.get_children():
            self.results_tree.selection_set(self.results_tree.get_children()[0])
            self.results_tree.focus(self.results_tree.get_children()[0])
            self._show_activity_detail()
        route = self.network._ordenar_ruta_critica()
        self.critical_var.set("  ›  ".join(route) if route else "No se encontró ruta crítica")
        self.metric_vars["duration"].set(format_duration(self.network.duracion_proyecto))
        self.metric_vars["critical"].set(str(len(self.network.ruta_critica)))
        self.metric_vars["count"].set(str(len(self.network.activities)))
        alerts = sum(1 for a in self.network.activities.values() if not a.is_critical and a.ff < a.tf - 1e-9)
        self.metric_vars["alerts"].set(str(alerts))

    def _draw_charts(self):
        for tab in (self.network_tab, self.gantt_tab):
            for child in tab.winfo_children():
                child.destroy()
        output = os.path.join(os.path.dirname(__file__), "salidas")
        os.makedirs(output, exist_ok=True)
        network_path = os.path.join(output, "red_proyecto.png")
        gantt_path = os.path.join(output, "cronograma_proyecto.png")
        self.network.graficar_red(network_path)
        self.network.graficar_gantt(gantt_path)
        for tab, path, title in ((self.network_tab, network_path, "RED DE PRECEDENCIAS"), (self.gantt_tab, gantt_path, "CRONOGRAMA DE ACTIVIDADES")):
            tab.rowconfigure(1, weight=1)
            tab.columnconfigure(0, weight=1)
            bar = ttk.Frame(tab, style="Panel.TFrame")
            bar.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
            ttk.Label(bar, text=title, style="CardCaption.TLabel").pack(side="left")
            ttk.Button(bar, text="Exportar PNG", command=lambda p=path: self._save_copy(p)).pack(side="right")
            figure = Figure(figsize=(10, 6), dpi=100, facecolor=COLORS["panel"])
            axis = figure.add_subplot(111)
            axis.set_facecolor(COLORS["panel"])
            image = plt_image(path)
            axis.imshow(image)
            axis.axis("off")
            canvas = FigureCanvasTkAgg(figure, master=tab)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
            self.chart_canvases[title] = canvas

    def _save_copy(self, source):
        target = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Imagen PNG", "*.png")])
        if target:
            with open(source, "rb") as src, open(target, "wb") as dst:
                dst.write(src.read())
            self.status_var.set(f"Imagen exportada: {os.path.basename(target)}")

    def _export_json(self):
        target = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Proyecto JSON", "*.json")])
        if target:
            with open(target, "w", encoding="utf-8") as file:
                json.dump(self.activities, file, ensure_ascii=False, indent=2)
            self.status_var.set("Proyecto exportado")

    def _import_json(self):
        source = filedialog.askopenfilename(filetypes=[("Proyecto JSON", "*.json")])
        if not source:
            return
        try:
            with open(source, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("El archivo debe contener una lista de actividades.")
            self.activities = data
            self._refresh_activity_tree()
            self._calculate()
        except (OSError, ValueError, TypeError, KeyError) as error:
            messagebox.showerror("Importación", f"No se pudo abrir el proyecto: {error}")


def plt_image(path):
    from matplotlib.image import imread
    return imread(path)


if __name__ == "__main__":
    CPMApp().mainloop()