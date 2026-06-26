import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Importaciones de lógica de negocio y persistencia
import core.fleet_manager as fleet_manager
import storage.pickle_manager as pickle_manager

# Importaciones de Matplotlib para la gráfica integrada
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class TrackFlotaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TrackFlota v1.0 - Gestión de Mantenimiento Local")
        self.geometry("1100x700")
        self.config(bg="#f4f6f9")
        
        # Estilos visuales modernos
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")
        
        # Estructura principal en dos grandes columnas (Izquierda: Control / Derecha: Gráfica)
        self.crear_componentes()
        self.actualizar_interfaz()

    def crear_componentes(self):
        # --- COLUMNA IZQUIERDA (Controles y Datos) ---
        panel_izquierdo = tk.Frame(self, bg="#f4f6f9")
        panel_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 1. INDICADORES CLAVE (KPIs)
        self.frame_kpis = tk.Frame(panel_izquierdo, bg="#f4f6f9")
        self.frame_kpis.pack(fill=tk.X, pady=10)
        
        self.lbl_total = tk.Label(self.frame_kpis, text="Total: 0", font=("Arial", 12, "bold"), bg="#34495e", fg="white", width=12, pady=10)
        self.lbl_total.pack(side=tk.LEFT, padx=5)
        
        self.lbl_libres = tk.Label(self.frame_kpis, text="Libres: 0", font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", width=12, pady=10)
        self.lbl_libres.pack(side=tk.LEFT, padx=5)
        
        self.lbl_taller = tk.Label(self.frame_kpis, text="En Taller: 0", font=("Arial", 12, "bold"), bg="#e74c3c", fg="white", width=12, pady=10)
        self.lbl_taller.pack(side=tk.LEFT, padx=5)

        # 2. FORMULARIO DE REGISTRO Y ACCIONES
        frame_acciones = tk.LabelFrame(panel_izquierdo, text=" Gestión de Camiones ", font=("Arial", 10, "bold"), bg="white", pady=10, padx=10)
        frame_acciones.pack(fill=tk.X, pady=10)
        
        tk.Label(frame_acciones, text="Placa:", bg="white").grid(row=0, column=0, sticky="w", padx=5)
        self.ent_placa = tk.Entry(frame_acciones, width=15)
        self.ent_placa.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_acciones, text="Modelo:", bg="white").grid(row=0, column=2, sticky="w", padx=5)
        self.ent_modelo = tk.Entry(frame_acciones, width=15)
        self.ent_modelo.grid(row=0, column=3, padx=5, pady=5)
        
        btn_registrar = tk.Button(frame_acciones, text="Registrar Nuevo", command=self.accion_registrar, bg="#3498db", fg="white", relief="flat")
        btn_registrar.grid(row=0, column=4, padx=10)
        
        # Botones de cambio de estado
        btn_entrar_taller = tk.Button(frame_acciones, text="📥 Ingresar a Taller", command=self.accion_ingresar_taller, bg="#e67e22", fg="white", relief="flat", font=("Arial", 9, "bold"))
        btn_entrar_taller.grid(row=1, column=1, columnspan=2, sticky="ew", pady=10, padx=5)
        btn_liberar = tk.Button(frame_acciones, text="📤 Dar Salida / Liberar", command=self.accion_liberar, bg="#2ca02c", fg="white", relief="flat", font=("Arial", 9, "bold"))
        btn_liberar.grid(row=1, column=3, columnspan=2, sticky="ew", pady=10, padx=5)
        btn_eliminar = tk.Button(frame_acciones, text="❌ Eliminar Camión", command=self.accion_eliminar, bg="#c0392b", fg="white", relief="flat", font=("Arial", 9, "bold"))
        btn_eliminar.grid(row=2, column=1, columnspan=2, sticky="ew", pady=5, padx=5)
        btn_cerrar = tk.Button(frame_acciones, text="🚪 Cerrar Programa", command=self.accion_cerrar_seguro, bg="#7f8c8d", fg="white", relief="flat", font=("Arial", 9, "bold"))
        btn_cerrar.grid(row=2, column=3, columnspan=2, sticky="ew", pady=5, padx=5)
        
        # 3. SISTEMA DE PESTAÑAS PARA LAS TABLAS (Modificado para ver todos los camiones)
        frame_tablas_container = tk.LabelFrame(panel_izquierdo, text=" Visores de Flota ", font=("Arial", 10, "bold"), bg="white", pady=5, padx=5)
        frame_tablas_container.pack(fill=tk.BOTH, expand=True, pady=10)

        notebook = ttk.Notebook(frame_tablas_container)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña A: Solo camiones en taller
        pestana_taller = tk.Frame(notebook, bg="white")
        notebook.add(pestana_taller, text=" En Mantenimiento ")
        
        self.tabla = ttk.Treeview(pestana_taller, columns=("Modelo", "Días en Taller"), show="headings")
        self.tabla.heading("Modelo", text="Modelo / Descripción")
        self.tabla.heading("Días en Taller", text="Días Transcurridos")
        self.tabla.pack(fill=tk.BOTH, expand=True)

        # 🆕 NUEVO: Pestaña B: Todos los camiones registrados
        pestana_todos = tk.Frame(notebook, bg="white")
        notebook.add(pestana_todos, text=" Todos los Camiones registrados ")

        self.tabla_todos = ttk.Treeview(pestana_todos, columns=("Modelo", "Estado", "Ingreso"), show="headings")
        self.tabla_todos.heading("Modelo", text="Camión (Placa - Modelo)")
        self.tabla_todos.heading("Estado", text="Estado Actual")
        self.tabla_todos.heading("Ingreso", text="Fecha de Ingreso a Taller")
        self.tabla_todos.pack(fill=tk.BOTH, expand=True)
        # --- COLUMNA DERECHA (Panel Analítico de Gráficos) ---
        self.panel_derecho = tk.LabelFrame(self, text=" Histórico Acumulado del Mes (Pickle) ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        self.panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Inicializamos la figura de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas_grafica = FigureCanvasTkAgg(self.fig, master=self.panel_derecho)
        self.canvas_grafica.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pestaña C: Informes y Acumulados
        pestana_informes = tk.Frame(notebook, bg="white")
        notebook.add(pestana_informes, text=" Informes / Acumulados ")

        self.tabla_informes = ttk.Treeview(pestana_informes, columns=("Modelo", "Acumulado"), show="headings")
        self.tabla_informes.heading("Modelo", text="Camión (Placa - Modelo)")
        self.tabla_informes.heading("Acumulado", text="Días Totales en Taller (Histórico)")
        self.tabla_informes.pack(fill=tk.BOTH, expand=True)
    # --- LÓGICA DE INTERFAZ Y REFRESH DINÁMICO ---
    def actualizar_interfaz(self):
        """Refresca los KPIs, ambas tablas (Taller y Todos) y la gráfica de barras."""
        metricas = fleet_manager.obtener_metricas_dashboard()
        
        # Actualizar Etiquetas de KPI
        self.lbl_total.config(text=f"Total: {metricas['total']}")
        self.lbl_libres.config(text=f"Libres: {metricas['libres']}")
        self.lbl_taller.config(text=f"En Taller: {metricas['mantenimiento']}")
        
        # 1. Actualizar Tabla de camiones en Taller
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for c in metricas['lista_taller']:
            # Usamos la placa como ID de la fila
            self.tabla.insert("", tk.END, iid=c['placa'], values=(f"{c['placa']} - {c['modelo']}", f"{c['dias_actuales']} días"))
            
        # 2. Actualizar Tabla de TODOS los camiones registrados
        import database.queries as queries
        for item in self.tabla_todos.get_children():
            self.tabla_todos.delete(item)
            
        todos_los_camiones = queries.obtener_todos_los_camiones()
        for c in todos_los_camiones:
            placa, modelo, estado, fecha_ingreso = c
            fecha_mostrar = fecha_ingreso if fecha_ingreso else "N/A (Disponible)"
            
            # 🆕 CORREGIDO: Quitamos el prefijo 'all_' y dejamos solo la placa limpia como ID
            self.tabla_todos.insert("", tk.END, iid=placa, values=(f"{placa} - {modelo}", estado, fecha_mostrar))
            
        # Actualizar Gráfica de Matplotlib desde el Pickle
        self.dibujar_grafica()

    def dibujar_grafica(self):
        """Lee el pickle del mes actual y guarda automáticamente el reporte si cambia el mes."""
        self.ax.clear()
        
        import os
        from datetime import datetime, timedelta
        
        # 1. Obtener fechas clave
        fecha_hoy = datetime.now()
        mes_actual_str = fecha_hoy.strftime("%Y-%m")
        
        # Truco: Averiguar si hoy es el último día del mes
        # Le sumamos 1 día a hoy. Si el mes de mañana es diferente al de hoy, ¡hoy es fin de mes!
        manana = fecha_hoy + timedelta(days=1)
        es_ultimo_dia_del_mes = manana.month != fecha_hoy.month
        
        # 2. Cargar datos del Pickle
        historial = pickle_manager.cargar_historial()
        datos_mes = historial.get(mes_actual_str, {})
        
        # 3. RENDERIZADO DE LA GRÁFICA (Igual que antes)
        if datos_mes:
            placas = list(datos_mes.keys())
            dias = list(datos_mes.values())
            barras = self.ax.bar(placas, dias, color="#e74c3c")
            self.ax.set_ylabel("Días Totales Acumulados")
            self.ax.set_title(f"Mantenimiento Acumulado - {mes_actual_str}")
            self.ax.tick_params(axis='x', rotation=45)
            self.ax.bar_label(barras, fmt='%.1f d')
            
            # 🆕 GUARDADO AUTOMÁTICO INTELIGENTE
            # Si es el último día del mes, guardamos una foto fija para que no se pierda mañana
            if es_ultimo_dia_del_mes:
                os.makedirs("reportes_mensuales", exist_ok=True)
                ruta_reporte = f"reportes_mensuales/cierre_{mes_actual_str}.png"
                
                # Solo la guardamos si el archivo no existe ya (para no sobreescribir mil veces el mismo día)
                if not os.path.exists(ruta_reporte):
                    self.fig.savefig(ruta_reporte)
                    print(f"[Sistema] ¡Fin de mes detectado! Gráfica guardada en {ruta_reporte}")
        else:
            self.ax.text(0.5, 0.5, "Sin registros históricos\nen el mes actual.", 
                        ha='center', va='center', fontsize=11, color="gray")
            self.ax.set_title(f"Mantenimiento Acumulado - {mes_actual_str}")

        self.fig.tight_layout()
        self.canvas_grafica.draw()

    # --- BOTONES DE ACCIÓN ---
    def accion_registrar(self):
        placa = self.ent_placa.get()
        modelo = self.ent_modelo.get()
        exito, msg = fleet_manager.registrar_nuevo_camion(placa, modelo)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.ent_placa.delete(0, tk.END)
            self.ent_modelo.delete(0, tk.END)
            self.actualizar_interfaz()
        else:
            messagebox.showerror("Error", msg)

    def accion_ingresar_taller(self):
        # Se puede escribir la placa o seleccionarla desde la tabla de forma inteligente
        placa = self.ent_placa.get().upper().strip()
        if not placa:
            messagebox.showwarning("Atención", "Por favor ingresa una placa en el formulario.")
            return
            
        exito, msg = fleet_manager.enviar_a_mantenimiento(placa)
        if exito:
            messagebox.showinfo("Taller", msg)
            self.actualizar_interfaz()
        else:
            messagebox.showerror("Error", msg)

    def accion_liberar(self):
        # Intenta obtener la placa de la selección de la tabla, si no, del campo de texto
        seleccion = self.tabla.selection()
        placa = seleccion[0] if seleccion else self.ent_placa.get().upper().strip()
        
        if not placa:
            messagebox.showwarning("Atención", "Selecciona un camión de la tabla o escribe su placa.")
            return
            
        exito, msg = fleet_manager.liberar_de_mantenimiento(placa)
        if exito:
            messagebox.showinfo("Vehículo Libre", msg)
            self.actualizar_interfaz()
        else:
            messagebox.showerror("Error", msg)
            
    def accion_eliminar(self):
        """Obtiene la placa seleccionada o escrita y la borra de SQLite tras confirmar."""
        seleccion = self.tabla.selection()
        placa = seleccion[0] if seleccion else self.ent_placa.get().upper().strip()
        
        if not placa:
            messagebox.showwarning("Atención", "Selecciona un camión de la tabla o escribe su placa para eliminarlo.")
            return
            
        # Preguntar al usuario para evitar accidentes
        confirmar = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar permanentemente el camión {placa}?")
        
        if confirmar:
            import database.queries as queries
            queries.eliminar_camion_por_placa(placa)
            messagebox.showinfo("Eliminado", f"El camión {placa} ha sido removido del sistema.")
            self.actualizar_interfaz()

    def accion_cerrar_seguro(self):
        """Garantiza el guardado de datos pendientes (si los hay) y cierra la app limpiamente."""
        # Como nuestra app guarda en SQLite en tiempo real y el Pickle se actualiza al liberar los camiones, 
        # los datos ya están 100% seguros en el disco. Solo notificamos y destruimos la ventana.
        confirmar = messagebox.askyesno("Salir", "¿Deseas cerrar TrackFlota?")
        if confirmar:
            self.destroy()
            import sys
            sys.exit(0)


def arrancar_aplicacion():
    app = TrackFlotaApp()
    app.mainloop()