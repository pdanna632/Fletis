import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os

# Importaciones de lógica de negocio y persistencia
import core.fleet_manager as fleet_manager
import storage.pickle_manager as pickle_manager

class TrackFlotaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TrackFlota v1.2 - Analítica de Mantenimiento Local")
        self.geometry("1200x750")
        
        # 🎨 PALETA DE COLORES MODERNA (Flat UI / Dark-Light Corporate)
        self.COLOR_BG = "#F8FAFC"          # Fondo general gris muy claro
        self.COLOR_CARD = "#FFFFFF"        # Fondo de contenedores (Blanco puro)
        self.COLOR_PRIMARY = "#1E293B"     # Azul oscuro pizarra (Títulos y botones principales)
        self.COLOR_ACCENT = "#3B82F6"      # Azul brillante (Registrar)
        self.COLOR_TALLER = "#EF4444"      # Rojo moderno (Ingresar a taller / Gráfica)
        self.COLOR_LIBRE = "#10B981"       # Verde esmeralda (Liberar)
        self.COLOR_TEXT = "#334155"        # Gris oscuro para textos principales
        
        self.config(bg=self.COLOR_BG)
        
        # --- CONFIGURACIÓN DE ESTILOS TTK (Componentes nativos) ---
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")
        
        # Customizar pestañas (Notebook)
        self.estilo.configure("TNotebook", background=self.COLOR_BG, borderwidth=0)
        self.estilo.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 6], background="#E2E8F0", foreground="#64748B")
        self.estilo.map("TNotebook.Tab", background=[("selected", self.COLOR_CARD)], foreground=[("selected", self.COLOR_PRIMARY)])
        
        # Customizar Tablas (Treeview)
        self.estilo.configure("Treeview", font=("Segoe UI", 10), rowheight=28, background=self.COLOR_CARD, fieldbackground=self.COLOR_CARD, foreground=self.COLOR_TEXT)
        self.estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#F1F5F9", foreground=self.COLOR_PRIMARY, relief="flat")
        self.estilo.map("Treeview", background=[("selected", "#E2E8F0")], foreground=[("selected", self.COLOR_PRIMARY)])

        # Hacer la ventana principal responsiva
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_componentes()
        self.actualizar_interfaz()
        
        # Interceptar el cierre desde la X de la ventana
        self.protocol("WM_DELETE_WINDOW", self.accion_cerrar_seguro)

    def crear_componentes(self):
        # ─── COLUMNA IZQUIERDA: CONTROLES Y TABLAS ───
        panel_izquierdo = tk.Frame(self, bg=self.COLOR_BG)
        panel_izquierdo.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        panel_izquierdo.grid_rowconfigure(2, weight=1) # La tabla se estirará hacia abajo
        panel_izquierdo.grid_columnconfigure(0, weight=1)

        # 1. TARJETAS DE INDICADORES (KPIs elegantes sin bordes toscos)
        frame_kpis = tk.Frame(panel_izquierdo, bg=self.COLOR_BG)
        frame_kpis.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Forzar que los KPIs se distribuyan equitativamente
        for i in range(3): frame_kpis.grid_columnconfigure(i, weight=1)

        self.lbl_total = tk.Label(frame_kpis, text="Total: 0", font=("Segoe UI", 11, "bold"), bg=self.COLOR_PRIMARY, fg="white", height=2, bd=0, relief="flat")
        self.lbl_total.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.lbl_libres = tk.Label(frame_kpis, text="Libres: 0", font=("Segoe UI", 11, "bold"), bg=self.COLOR_LIBRE, fg="white", height=2, bd=0, relief="flat")
        self.lbl_libres.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.lbl_taller = tk.Label(frame_kpis, text="En Taller: 0", font=("Segoe UI", 11, "bold"), bg=self.COLOR_TALLER, fg="white", height=2, bd=0, relief="flat")
        self.lbl_taller.grid(row=0, column=2, padx=5, sticky="ew")

        # 2. PANEL DE ACCIONES (Formulario estilizado como Tarjeta Limpia)
        frame_acciones = tk.Frame(panel_izquierdo, bg=self.COLOR_CARD, padx=15, pady=15, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_acciones.grid(row=1, column=0, sticky="ew", pady=10)
        for i in range(4): frame_acciones.grid_columnconfigure(i, weight=1)

        # Inputs con tipografía moderna
        tk.Label(frame_acciones, text="Placa:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_TEXT).grid(row=0, column=0, sticky="w", padx=5)
        self.ent_placa = tk.Entry(frame_acciones, font=("Segoe UI", 10), bg="#F8FAFC", relief="flat", highlightbackground="#CBD5E1", highlightthickness=1)
        self.ent_placa.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        tk.Label(frame_acciones, text="Modelo:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_TEXT).grid(row=0, column=2, sticky="w", padx=5)
        self.ent_modelo = tk.Entry(frame_acciones, font=("Segoe UI", 10), bg="#F8FAFC", relief="flat", highlightbackground="#CBD5E1", highlightthickness=1)
        self.ent_modelo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Botones con estilo moderno (Flat, sin relieves anticuados)
        btn_registrar = tk.Button(frame_acciones, text="➕ Registrar Camión", command=self.accion_registrar, bg=self.COLOR_ACCENT, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", activebackground="#2563EB")
        btn_registrar.grid(row=0, column=4, padx=10, ipady=3)
        
        # Botones de estado en la fila inferior
        btn_entrar_taller = tk.Button(frame_acciones, text="📥 Ingresar a Taller", command=self.accion_ingresar_taller, bg=self.COLOR_PRIMARY, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2")
        btn_entrar_taller.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(15, 5), padx=5, ipady=4)
        
        btn_liberar = tk.Button(frame_acciones, text="📤 Dar Salida / Liberar", command=self.accion_liberar, bg=self.COLOR_LIBRE, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2")
        btn_liberar.grid(row=1, column=2, columnspan=2, sticky="ew", pady=(15, 5), padx=5, ipady=4)

        btn_eliminar = tk.Button(frame_acciones, text="❌ Eliminar", command=self.accion_eliminar, bg="#EFF6FF", fg=self.COLOR_TALLER, font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2")
        btn_eliminar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5, padx=5, ipady=3)

        btn_cerrar = tk.Button(frame_acciones, text="🚪 Cerrar Programa", command=self.accion_cerrar_seguro, bg="#F1F5F9", fg="#64748B", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2")
        btn_cerrar.grid(row=2, column=2, columnspan=2, sticky="ew", pady=5, padx=5, ipady=3)

        # 3. CONTENEDOR DE PESTAÑAS Y TABLAS
        frame_tablas_container = tk.Frame(panel_izquierdo, bg=self.COLOR_BG)
        frame_tablas_container.grid(row=2, column=0, sticky="nsew", pady=10)
        frame_tablas_container.grid_rowconfigure(0, weight=1)
        frame_tablas_container.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(frame_tablas_container)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Pestaña 1: Taller
        pestana_taller = tk.Frame(self.notebook, bg=self.COLOR_CARD)
        self.notebook.add(pestana_taller, text=" En Mantenimiento ")
        self.tabla = ttk.Treeview(pestana_taller, columns=("Modelo", "Días en Taller"), show="headings")
        self.tabla.heading("Modelo", text="Modelo / Descripción")
        self.tabla.heading("Días en Taller", text="Días Transcurridos")
        self.tabla.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Pestaña 2: Todos
        pestana_todos = tk.Frame(self.notebook, bg=self.COLOR_CARD)
        self.notebook.add(pestana_todos, text=" Todos los Camiones ")
        self.tabla_todos = ttk.Treeview(pestana_todos, columns=("Modelo", "Estado", "Ingreso"), show="headings")
        self.tabla_todos.heading("Modelo", text="Camión (Placa - Modelo)")
        self.tabla_todos.heading("Estado", text="Estado Actual")
        self.tabla_todos.heading("Ingreso", text="Fecha de Ingreso")
        self.tabla_todos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Pestaña 3: Informes Consolidados
        pestana_informes = tk.Frame(self.notebook, bg=self.COLOR_CARD)
        self.notebook.add(pestana_informes, text=" Histórico Acumulado ")
        self.tabla_informes = ttk.Treeview(pestana_informes, columns=("Modelo", "Acumulado"), show="headings")
        self.tabla_informes.heading("Modelo", text="Camión (Placa - Modelo)")
        self.tabla_informes.heading("Acumulado", text="Días Totales Históricos en Taller")
        self.tabla_informes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


        # ─── COLUMNA DERECHA: PANEL ANALÍTICO (MATPLOTLIB) ───
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.pyplot as plt

        self.panel_derecho = tk.Frame(self, bg=self.COLOR_CARD, highlightbackground="#E2E8F0", highlightthickness=1)
        self.panel_derecho.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.panel_derecho.grid_rowconfigure(0, weight=1)
        self.panel_derecho.grid_columnconfigure(0, weight=1)
        
        # Configurar figura limpia en Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 5), dpi=100)
        self.fig.patch.set_facecolor(self.COLOR_CARD) # Fondo de la figura blanco líquido
        self.canvas_grafica = FigureCanvasTkAgg(self.fig, master=self.panel_derecho)
        self.canvas_grafica.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)


    # ─── LÓGICA DE REFRESH DINÁMICO Y ACTUALIZACIONES ───
    def actualizar_interfaz(self):
        """Refresca las métricas, las tres tablas del sistema y el gráfico analítico."""
        metricas = fleet_manager.obtener_metricas_dashboard()
        
        # Actualizar KPIs
        self.lbl_total.config(text=f"Total: {metricas['total']} Camiones")
        self.lbl_libres.config(text=f"Disponibles: {metricas['libres']}")
        self.lbl_taller.config(text=f"En Taller: {metricas['mantenimiento']}")
        
        # 1. Tabla: Solo en taller
        for item in self.tabla.get_children(): self.tabla.delete(item)
        for c in metricas['lista_taller']:
            self.tabla.insert("", tk.END, iid=c['placa'], values=(f"{c['placa']} - {c['modelo']}", f"⏱️ {c['dias_actuales']} días"))
            
        # 2. Tabla: Todos los registrados
        import database.queries as queries
        for item in self.tabla_todos.get_children(): self.tabla_todos.delete(item)
        
        todos_los_camiones = queries.obtener_todos_los_camiones()
        for c in todos_los_camiones:
            placa, modelo, estado, fecha_ingreso = c
            fecha_mostrar = fecha_ingreso if fecha_ingreso else "✅ Disponible para Ruta"
            estado_icono = "🔴 Taller" if estado == "Mantenimiento" else "🟢 Libre"
            self.tabla_todos.insert("", tk.END, iid=placa, values=(f"{placa} - {modelo}", estado_icono, fecha_mostrar))
            
        # 3. Tabla: Histórico acumulado desde el Pickle
        for item in self.tabla_informes.get_children(): self.tabla_informes.delete(item)
        historico_pickle = pickle_manager.obtener_resumen_historico()
        
        # Mapeamos las placas con sus nombres para que sea más legible en informes
        dicc_modelos = {c[0]: c[1] for c in todos_los_camiones}
        for placa, dias_totales in historico_pickle.items():
            modelo_camion = dicc_modelos.get(placa, "Desconocido")
            self.tabla_informes.insert("", tk.END, iid=f"rep_{placa}", values=(f"{placa} - {modelo_camion}", f"📊 {round(dias_totales, 2)} días totales"))

        # 4. Redibujar Gráfica
        self.dibujar_grafica()

    def dibujar_grafica(self):
        """Renderiza el gráfico de barras y gestiona el cierre mensual automatizado."""
        self.ax.clear()
        self.ax.set_facecolor(self.COLOR_CARD)
        
        fecha_hoy = datetime.now()
        mes_actual_str = fecha_hoy.strftime("%Y-%m")
        
        # Algoritmo de fin de mes
        manana = fecha_hoy + timedelta(days=1)
        es_ultimo_dia_del_mes = manana.month != fecha_hoy.month
        
        historial = pickle_manager.cargar_historial()
        datos_mes = historial.get(mes_actual_str, {})
        
        if datos_mes:
            placas = list(datos_mes.keys())
            dias = list(datos_mes.values())
            
            # Gráfico de barras estilizado
            barras = self.ax.bar(placas, dias, color=self.COLOR_TALLER, width=0.5, edgecolor="#B91C1C", linewidth=1)
            self.ax.set_ylabel("Días Acumulados en el Mes", fontname="Segoe UI", fontsize=10, fontweight="bold", color=self.COLOR_TEXT)
            self.ax.set_title(f"Mantenimiento Mensual: {mes_actual_str}", fontname="Segoe UI", fontsize=12, fontweight="bold", color=self.COLOR_PRIMARY)
            self.ax.tick_params(axis='x', rotation=35, labelsize=9, labelcolor=self.COLOR_TEXT)
            self.ax.bar_label(barras, fmt='%.1f d', padding=3, fontname="Segoe UI", fontsize=9, color=self.COLOR_TEXT)
            
            # Limpiar bordes toscos de la gráfica (estilo minimalista)
            for spine in ["top", "right", "left"]: self.ax.spines[spine].set_visible(False)
            self.ax.spines["bottom"].set_color("#CBD5E1")
            
            # Guardar el .png si es el último día del mes de forma silenciosa
            if es_ultimo_dia_del_mes:
                os.makedirs("reportes_mensuales", exist_ok=True)
                ruta_reporte = f"reportes_mensuales/cierre_{mes_actual_str}.png"
                if not os.path.exists(ruta_reporte):
                    self.fig.savefig(ruta_reporte)
                    print(f"[Sistema] Resumen mensual guardado de forma segura en: {ruta_reporte}")
        else:
            self.ax.text(0.5, 0.5, "Monitoreo mensual activo.\nSin registros históricos en este periodo.", 
                        ha='center', va='center', fontname="Segoe UI", fontsize=10, color="#94A3B8")
            self.ax.set_title(f"Mantenimiento Mensual: {mes_actual_str}", fontname="Segoe UI", fontsize=11, fontweight="bold", color=self.COLOR_PRIMARY)
            for spine in self.ax.spines.values(): spine.set_visible(False)
            self.ax.get_xaxis().set_visible(False)
            self.ax.get_yaxis().set_visible(False)

        self.fig.tight_layout()
        self.canvas_grafica.draw()

    # ─── CONTROLADORES DE ACCIÓN INTERACTIVOS ───
    def obtener_placa_activa(self):
        """Helper inteligente para obtener la placa seleccionada en cualquier pestaña o escrita."""
        pestana_activa = self.notebook.index(self.notebook.select())
        placa = ""
        
        if pestana_activa == 0 and self.tabla.selection():
            placa = self.tabla.selection()[0]
        elif pestana_activa == 1 and self.tabla_todos.selection():
            placa = self.tabla_todos.selection()[0]
            
        if not placa:
            placa = self.ent_placa.get().upper().strip()
            
        return placa

    def accion_registrar(self):
        placa = self.ent_placa.get().upper().strip()
        modelo = self.ent_modelo.get().strip()
        
        if not placa or not modelo:
            messagebox.showwarning("Atención", "Por favor completa los campos de Placa y Modelo.")
            return
            
        exito, msg = fleet_manager.registrar_nuevo_camion(placa, modelo)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.ent_placa.delete(0, tk.END)
            self.ent_modelo.delete(0, tk.END)
            self.actualizar_interfaz()
        else:
            messagebox.showerror("Error", msg)

    def accion_ingresar_taller(self):
        placa = self.obtener_placa_activa()
        if not placa:
            messagebox.showwarning("Atención", "Seleccione un camión de las listas o digite la placa.")
            return
        exito, msg = fleet_manager.enviar_a_mantenimiento(placa)
        if exito:
            messagebox.showinfo("Ingreso Taller", msg)
            self.actualizar_interfaz()
        else:
            messagebox.showerror("Error", msg)

    def accion_liberar(self):
        placa = self.obtener_placa_activa()
        if not placa:
            messagebox.showwarning("Atención", "Seleccione un camión de las listas o digite la placa.")
            return
        exito, msg = fleet_manager.liberar_de_mantenimiento(placa)
        if exito:
            messagebox.showinfo("Salida Taller", msg)
            self.actualizar_interfaz()
        else:
            messagebox.showerror("Error", msg)

    def accion_eliminar(self):
        placa = self.obtener_placa_activa()
        if not placa:
            messagebox.showwarning("Atención", "Seleccione el camión que desea eliminar de la base de datos.")
            return
            
        confirmar = messagebox.askyesno("Confirmar", f"¿Desea borrar de forma permanente el camión {placa}?")
        if confirmar:
            import database.queries as queries
            queries.eliminar_camion_por_placa(placa)
            messagebox.showinfo("Eliminado", "Registro borrado del sistema.")
            self.actualizar_interfaz()

    def accion_cerrar_seguro(self):
        confirmar = messagebox.askyesno("Salir", "¿Seguro que desea cerrar TrackFlota?")
        if confirmar:
            self.destroy()
            import sys
            sys.exit(0)

def arrancar_aplicacion():
    app = TrackFlotaApp()
    app.mainloop()