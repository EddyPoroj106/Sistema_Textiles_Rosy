import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import webbrowser

class RecursosHumanos:
    def __init__(self, root=None):
        self.root = root
        self.window = tk.Toplevel(root) if root else tk.Tk()
        self.window.title("Recursos Humanos - Textiles Rosy")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        self.callback_nomina = None
        
        # Control para evitar múltiples instancias
        self.window.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        
        # Configuración de archivos
        self.data_dir = "data_rrhh"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.empleados_file = os.path.join(self.data_dir, "empleados.json")
        self.seleccionados_file = os.path.join(self.data_dir, "seleccionados.json")
        self.contratados_file = os.path.join(self.data_dir, "contratados.json")
        
        # Cargar datos
        self.cargar_datos()
        
        # Áreas disponibles
        self.areas = {
            "Administración": "A",
            "Producción": "P",
            "Ventas": "V",
            "Logística": "L",
            "Recursos Humanos": "RH",
            "Contabilidad": "C"
        }
        
        # Configurar interfaz
        self.conf_estilo()
        self.conf_gui()
    
    def cargar_datos(self):
        """Carga los datos de empleados, seleccionados y contratados"""
        self.empleados = self._cargar_json(self.empleados_file, {})
        self.seleccionados = self._cargar_json(self.seleccionados_file, [])
        self.contratados = self._cargar_json(self.contratados_file, {})
    
    def _cargar_json(self, file, default):
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def guardar_datos(self):
        """Guarda todos los datos en archivos JSON"""
        with open(self.empleados_file, 'w') as f:
            json.dump(self.empleados, f, indent=4)
        with open(self.seleccionados_file, 'w') as f:
            json.dump(self.seleccionados, f, indent=4)
        with open(self.contratados_file, 'w') as f:
            json.dump(self.contratados, f, indent=4)
    
    def conf_estilo(self):
        """Configura el estilo visual mejorado"""
        style = ttk.Style()
        style.theme_use('clam')
        
        PRIMARY_COLOR = "#3498db"
        SECONDARY_COLOR = "#2c3e50"
        ACCENT_COLOR = "#e74c3c"
        BG_COLOR = "#ecf0f1"
        LIGHT_BG = "#ffffff"
        
        style.configure(".", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=SECONDARY_COLOR, font=('Arial', 9))
        style.configure("TButton", background=PRIMARY_COLOR, foreground="white", font=('Arial', 9), padding=5)
        style.configure("Treeview", fieldbackground=LIGHT_BG, background=LIGHT_BG, font=('Arial', 9), rowheight=25)
        style.configure("Treeview.Heading", background=PRIMARY_COLOR, foreground="white", font=('Arial', 9, 'bold'))
        style.configure("TNotebook", background=BG_COLOR)
        style.configure("TNotebook.Tab", background="#bdc3c7", padding=[10, 5], font=('Arial', 9, 'bold'))
        style.map("TNotebook.Tab", background=[("selected", PRIMARY_COLOR)], foreground=[("selected", "white")])
        
        style.configure("Title.TLabel", font=('Arial', 12, 'bold'), foreground=PRIMARY_COLOR)
        style.configure("Important.TLabel", font=('Arial', 10, 'bold'))
        style.configure("Accent.TButton", background=ACCENT_COLOR)
        style.configure("Success.TButton", background="#2ecc71")
        style.configure("Light.TFrame", background=LIGHT_BG)
    
    def conf_gui(self):
        """Configura la interfaz gráfica principal optimizada"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Header con logo y título
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="🧑‍💼", font=('Arial', 24)).pack(side='left', padx=5)
        ttk.Label(header_frame, text="Recursos Humanos", font=('Arial', 16, 'bold'), foreground="#2c3e50").pack(side='left')
        
        # Notebook para pestañas con mejor distribución
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both')
        
        # Pestañas con nuevo diseño
        self.crear_pestania_reclutamiento()
        self.crear_pestania_seleccion()
        self.crear_pestania_contratacion()
        self.crear_pestania_planilla()
        
        # Barra de estado
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief='sunken', padding=5)
        status_bar.pack(fill='x', pady=(5, 0))
        self.actualizar_status("Sistema listo")
    
    def actualizar_status(self, mensaje):
        self.status_var.set(f"🟢 {mensaje} | Empleados: {len(self.empleados)} | Seleccionados: {len(self.seleccionados)} | Contratados: {len(self.contratados)}")
    
    # --------------------------------------------
    # Reclutamiento - Diseño mejorado
    # --------------------------------------------
    def crear_pestania_reclutamiento(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="📝 Reclutamiento")
        
        # Contenedor principal con scroll
        container = ttk.Frame(frame)
        container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenido del formulario
        form_frame = ttk.Frame(scrollable_frame, padding=10, style="Light.TFrame")
        form_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Nuevo Empleado", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        # Sección de información básica
        info_frame = ttk.LabelFrame(form_frame, text=" Información Básica ", padding=10)
        info_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        
        ttk.Label(info_frame, text="Nombre completo:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.nombre_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.nombre_var, width=40).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(info_frame, text="Identificación:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.identificacion_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.identificacion_var, width=20).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(info_frame, text="Área de trabajo:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.area_var = tk.StringVar()
        self.area_cb = ttk.Combobox(info_frame, textvariable=self.area_var, 
                                  values=list(self.areas.keys()), state='readonly', width=20)
        self.area_cb.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Sección de documentos
        doc_frame = ttk.LabelFrame(form_frame, text=" Documentación Requerida ", padding=10)
        doc_frame.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
        
        self.doc_identificacion = ""
        self.doc_curriculum = ""
        
        ttk.Button(doc_frame, text="📄 Subir Identificación", 
                  command=lambda: self.subir_documento("identificacion"),
                  style="TButton").grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(doc_frame, text="📑 Subir Curriculum", 
                  command=lambda: self.subir_documento("curriculum"),
                  style="TButton").grid(row=0, column=1, padx=5, pady=5)
        
        self.doc_status_frame = ttk.Frame(doc_frame)
        self.doc_status_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Label(self.doc_status_frame, text="Estado documentos:").pack(side='left')
        self.identificacion_status = ttk.Label(self.doc_status_frame, text="❌", foreground="red")
        self.identificacion_status.pack(side='left', padx=5)
        self.curriculum_status = ttk.Label(self.doc_status_frame, text="❌", foreground="red")
        self.curriculum_status.pack(side='left', padx=5)
        
        # Sección de botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, pady=20)
        
        ttk.Button(button_frame, text="➕ Registrar Empleado", 
                  command=self.registrar_empleado, 
                  style="Success.TButton").pack(pady=10, ipadx=20, ipady=5)
    
    def subir_documento(self, tipo):
        file = filedialog.askopenfilename(
            title=f"Seleccionar documento de {tipo}",
            filetypes=[("PDF files", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if file:
            if tipo == "identificacion":
                self.doc_identificacion = file
                self.identificacion_status.config(text="✔️", foreground="green")
            else:
                self.doc_curriculum = file
                self.curriculum_status.config(text="✔️", foreground="green")
            self.actualizar_status(f"Documento {tipo} subido correctamente")
    
    def registrar_empleado(self):
        nombre = self.nombre_var.get().strip()
        identificacion = self.identificacion_var.get().strip()
        area_nombre = self.area_var.get()
        
        if not nombre or not identificacion or not area_nombre:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        if not self.doc_identificacion or not self.doc_curriculum:
            messagebox.showerror("Error", "Debe subir ambos documentos")
            return
        
        area_code = self.areas[area_nombre]
        codigo = self.generar_codigo(area_code)
        
        nuevo_empleado = {
            "codigo": codigo,
            "nombre": nombre,
            "identificacion": identificacion,
            "area": area_nombre,
            "doc_identificacion": self.doc_identificacion,
            "doc_curriculum": self.doc_curriculum,
            "fecha_registro": datetime.now().strftime("%Y-%m-%d"),
            "estado": "Reclutado"
        }
        
        self.empleados[codigo] = nuevo_empleado
        self.guardar_datos()
        
        messagebox.showinfo("Éxito", f"Empleado registrado con código: {codigo}")
        self.limpiar_formulario_reclutamiento()
        self.actualizar_status(f"Nuevo empleado registrado: {nombre}")
    
    def limpiar_formulario_reclutamiento(self):
        self.nombre_var.set("")
        self.identificacion_var.set("")
        self.area_var.set("")
        self.doc_identificacion = ""
        self.doc_curriculum = ""
        self.identificacion_status.config(text="❌", foreground="red")
        self.curriculum_status.config(text="❌", foreground="red")
    
    # --------------------------------------------
    # Selección - Diseño mejorado
    # --------------------------------------------
    def crear_pestania_seleccion(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔍 Selección")
        
        # Frame de búsqueda y acciones
        search_frame = ttk.Frame(frame, padding=10)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Buscar candidato:", style="Important.TLabel").pack(side='left', padx=5)
        
        self.codigo_seleccion_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.codigo_seleccion_var, width=15)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<Return>', lambda e: self.buscar_empleado())
        
        ttk.Button(search_frame, text="Buscar", command=self.buscar_empleado).pack(side='left', padx=5)
        
        # Resultados en paneles
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Panel izquierdo - Información del empleado
        info_frame = ttk.LabelFrame(results_frame, text=" Información del Candidato ", padding=10)
        info_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        self.empleado_info_text = tk.Text(info_frame, width=40, height=10, wrap='word', font=('Arial', 9))
        self.empleado_info_text.pack(fill='both', expand=True)
        
        # Panel derecho - Documentos y acciones
        action_frame = ttk.LabelFrame(results_frame, text=" Acciones ", padding=10)
        action_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        ttk.Button(action_frame, text="📄 Ver Identificación", 
                  command=lambda: self.ver_documento("identificacion")).pack(fill='x', pady=5)
        ttk.Button(action_frame, text="📑 Ver Curriculum", 
                  command=lambda: self.ver_documento("curriculum")).pack(fill='x', pady=5)
        
        ttk.Separator(action_frame).pack(fill='x', pady=10)
        
        ttk.Button(action_frame, text="✅ Seleccionar para Contratación", 
                  command=self.agregar_a_seleccion, style="Success.TButton").pack(fill='x', pady=5, ipady=5)
        
        # Lista de seleccionados
        selected_frame = ttk.LabelFrame(frame, text=" Candidatos Seleccionados ", padding=10)
        selected_frame.pack(fill='both', padx=10, pady=10)
        
        columns = ('codigo', 'nombre', 'area', 'fecha_seleccion')
        self.tree_seleccion = ttk.Treeview(selected_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            self.tree_seleccion.heading(col, text=col.capitalize())
            self.tree_seleccion.column(col, width=120, anchor='w')
        
        scrollbar = ttk.Scrollbar(selected_frame, orient='vertical', command=self.tree_seleccion.yview)
        self.tree_seleccion.configure(yscrollcommand=scrollbar.set)
        
        self.tree_seleccion.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Cargar seleccionados existentes
        self.actualizar_lista_seleccionados()
    
    def buscar_empleado(self):
        codigo = self.codigo_seleccion_var.get().strip()
        if not codigo:
            messagebox.showerror("Error", "Ingrese un código de empleado")
            return
        
        empleado = self.empleados.get(codigo)
        if not empleado:
            messagebox.showerror("Error", "Empleado no encontrado")
            return
        
        self.empleado_actual = empleado
        
        # Mostrar información en el panel
        self.empleado_info_text.config(state='normal')
        self.empleado_info_text.delete(1.0, tk.END)
        
        info_text = f"""Código: {empleado['codigo']}
Nombre: {empleado['nombre']}
Identificación: {empleado['identificacion']}
Área: {empleado['area']}
Estado: {empleado.get('estado', 'N/A')}
Fecha Registro: {empleado.get('fecha_registro', 'N/A')}

Documentos:
- Identificación: {'✔️' if empleado.get('doc_identificacion') else '❌'}
- Curriculum: {'✔️' if empleado.get('doc_curriculum') else '❌'}
"""
        self.empleado_info_text.insert(tk.END, info_text)
        self.empleado_info_text.config(state='disabled')
        
        self.actualizar_status(f"Empleado encontrado: {empleado['nombre']}")
    
    def ver_documento(self, tipo):
        if not hasattr(self, 'empleado_actual'):
            messagebox.showerror("Error", "Primero busque un empleado")
            return
        
        doc_path = self.empleado_actual.get(f"doc_{tipo}", "")
        if not doc_path:
            messagebox.showerror("Error", f"No hay documento de {tipo} subido")
            return
        
        try:
            webbrowser.open(doc_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el documento: {str(e)}")
    
    def agregar_a_seleccion(self):
        if not hasattr(self, 'empleado_actual'):
            messagebox.showerror("Error", "Primero busque un empleado")
            return
        
        codigo = self.empleado_actual['codigo']
        if codigo in self.seleccionados:
            messagebox.showerror("Error", "Este empleado ya está en la lista de selección")
            return
        
        self.seleccionados.append(codigo)
        self.empleados[codigo]['estado'] = "Seleccionado"
        self.empleados[codigo]['fecha_seleccion'] = datetime.now().strftime("%Y-%m-%d")
        self.guardar_datos()
        
        self.actualizar_lista_seleccionados()
        messagebox.showinfo("Éxito", "Empleado agregado a la lista de selección")
        self.actualizar_status(f"Empleado seleccionado: {self.empleado_actual['nombre']}")
    
    def actualizar_lista_seleccionados(self):
        for item in self.tree_seleccion.get_children():
            self.tree_seleccion.delete(item)
            
        for codigo in self.seleccionados:
            emp = self.empleados.get(codigo, {})
            self.tree_seleccion.insert('', 'end', values=(
                codigo,
                emp.get('nombre', 'N/A'),
                emp.get('area', 'N/A'),
                emp.get('fecha_seleccion', 'N/A')
            ))
    
    # --------------------------------------------
    # Contratación - Diseño mejorado
    # --------------------------------------------
    def crear_pestania_contratacion(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📄 Contratación")
        
        # Frame de búsqueda
        search_frame = ttk.Frame(frame, padding=10)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Código del candidato seleccionado:", style="Important.TLabel").pack(side='left', padx=5)
        
        self.codigo_contratacion_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.codigo_contratacion_var, width=15).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Buscar", command=self.buscar_para_contratar).pack(side='left', padx=5)
        
        # Formulario de contratación
        form_frame = ttk.LabelFrame(frame, text=" Detalles de Contratación ", padding=15)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Primera fila
        row1 = ttk.Frame(form_frame)
        row1.pack(fill='x', pady=5)
        
        ttk.Label(row1, text="Sueldo Base:").pack(side='left', padx=5)
        self.sueldo_var = tk.DoubleVar()
        ttk.Entry(row1, textvariable=self.sueldo_var, width=15).pack(side='left', padx=5)
        
        ttk.Label(row1, text="Jornada:").pack(side='left', padx=5)
        self.jornada_var = tk.StringVar()
        ttk.Combobox(row1, textvariable=self.jornada_var, 
                    values=["Tiempo Completo", "Medio Tiempo", "Por Horas"], 
                    state='readonly', width=15).pack(side='left', padx=5)
        
        # Segunda fila
        row2 = ttk.Frame(form_frame)
        row2.pack(fill='x', pady=5)
        
        ttk.Label(row2, text="Comisión (%):").pack(side='left', padx=5)
        self.comision_var = tk.DoubleVar(value=0.0)
        ttk.Entry(row2, textvariable=self.comision_var, width=5).pack(side='left', padx=5)
        
        ttk.Label(row2, text="Tipo de Contrato:").pack(side='left', padx=5)
        self.tipo_contrato_var = tk.StringVar()
        ttk.Combobox(row2, textvariable=self.tipo_contrato_var,
                    values=["Indefinido", "Temporal", "Prueba", "Formación"],
                    state='readonly', width=12).pack(side='left', padx=5)
        
        # Documentos
        doc_frame = ttk.Frame(form_frame)
        doc_frame.pack(fill='x', pady=10)
        
        ttk.Button(doc_frame, text="📝 Subir Contrato PDF", 
                  command=self.subir_contrato).pack(side='left', padx=5)
        
        self.contrato_status = ttk.Label(doc_frame, text="❌ No subido", foreground="red")
        self.contrato_status.pack(side='left', padx=5)
        
        # Botón de contratación
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="✨ Formalizar Contratación", 
                  command=self.contratar_empleado, 
                  style="Success.TButton").pack(ipadx=20, ipady=5)
    
    def buscar_para_contratar(self):
        codigo = self.codigo_contratacion_var.get().strip()
        if not codigo:
            messagebox.showerror("Error", "Ingrese un código de empleado")
            return
        
        if codigo not in self.seleccionados:
            messagebox.showerror("Error", "Empleado no está en la lista de selección")
            return
        
        empleado = self.empleados.get(codigo)
        if not empleado:
            messagebox.showerror("Error", "Empleado no encontrado")
            return
        
        self.empleado_a_contratar = empleado
        messagebox.showinfo("Encontrado", f"Empleado {empleado['nombre']} listo para contratación")
        self.actualizar_status(f"Preparando contratación para: {empleado['nombre']}")
    
    def subir_contrato(self):
        file = filedialog.askopenfilename(
            title="Seleccionar contrato en PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file:
            self.contrato_path = file
            self.contrato_status.config(text="✔️ Subido", foreground="green")
            self.actualizar_status("Contrato subido correctamente")
    
    def contratar_empleado(self):
        if not hasattr(self, 'empleado_a_contratar'):
            messagebox.showerror("Error", "Primero busque un empleado para contratar")
            return
        
        try:
            sueldo = float(self.sueldo_var.get())
            jornada = self.jornada_var.get()
            comision = float(self.comision_var.get())
            tipo_contrato = self.tipo_contrato_var.get()
            
            if sueldo <= 0:
                raise ValueError("Sueldo debe ser positivo")
            if not jornada:
                raise ValueError("Seleccione una jornada")
            if comision < 0 or comision > 100:
                raise ValueError("Comisión debe estar entre 0 y 100")
            if not tipo_contrato:
                raise ValueError("Seleccione un tipo de contrato")
            if not hasattr(self, 'contrato_path'):
                raise ValueError("Debe subir el contrato")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
            return
        
        codigo = self.empleado_a_contratar['codigo']
        
        datos_contratacion = {
            "sueldo_base": sueldo,
            "jornada": jornada,
            "comision": comision,
            "tipo_contrato": tipo_contrato,
            "contrato_path": self.contrato_path,
            "fecha_contratacion": datetime.now().strftime("%Y-%m-%d"),
            "estado": "Contratado"
        }
        
        # Actualizar empleado
        self.empleados[codigo].update(datos_contratacion)
        self.empleados[codigo]['estado'] = "Contratado"
        
        # Agregar a contratados
        self.contratados[codigo] = self.empleados[codigo]
        
        # Quitar de seleccionados
        if codigo in self.seleccionados:
            self.seleccionados.remove(codigo)
        
        self.guardar_datos()
        messagebox.showinfo("Éxito", "Empleado contratado correctamente")
        self.actualizar_status(f"Contratación completada: {self.empleado_a_contratar['nombre']}")
        self.limpiar_formulario_contratacion()
    
    def limpiar_formulario_contratacion(self):
        self.codigo_contratacion_var.set("")
        self.sueldo_var.set(0)
        self.jornada_var.set("")
        self.comision_var.set(0)
        self.tipo_contrato_var.set("")
        if hasattr(self, 'contrato_path'):
            del self.contrato_path
        self.contrato_status.config(text="❌ No subido", foreground="red")
        if hasattr(self, 'empleado_a_contratar'):
            del self.empleado_a_contratar
    
    # --------------------------------------------
    # Planilla - Diseño mejorado
    # --------------------------------------------
    def crear_pestania_planilla(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💰 Planilla")
        
        # Frame de búsqueda
        search_frame = ttk.Frame(frame, padding=10)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Código del empleado contratado:", style="Important.TLabel").pack(side='left', padx=5)
        
        self.codigo_planilla_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.codigo_planilla_var, width=15).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Buscar", command=self.buscar_para_planilla).pack(side='left', padx=5)
        
        # Contenedor principal
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Panel izquierdo - Datos de cálculo
        calc_frame = ttk.LabelFrame(main_frame, text=" Datos para Cálculo ", padding=15)
        calc_frame.pack(side='left', fill='both', padx=5, pady=5)
        
        ttk.Label(calc_frame, text="Horas Extras:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.horas_extras_var = tk.IntVar(value=0)
        ttk.Entry(calc_frame, textvariable=self.horas_extras_var, width=8).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(calc_frame, text="Bono:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.bono_var = tk.DoubleVar(value=0.0)
        ttk.Entry(calc_frame, textvariable=self.bono_var, width=8).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(calc_frame, text="Adelantos:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.adelantos_var = tk.DoubleVar(value=0.0)
        ttk.Entry(calc_frame, textvariable=self.adelantos_var, width=8).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(calc_frame, text="Préstamos:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.prestamos_var = tk.DoubleVar(value=0.0)
        ttk.Entry(calc_frame, textvariable=self.prestamos_var, width=8).grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(calc_frame, text="Sanciones:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.sanciones_var = tk.DoubleVar(value=0.0)
        ttk.Entry(calc_frame, textvariable=self.sanciones_var, width=8).grid(row=4, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(calc_frame, text="🔄 Calcular Planilla", 
                  command=self.calcular_planilla, style="TButton").grid(row=5, column=0, columnspan=2, pady=10)
        
        # Panel derecho - Resultados
        result_frame = ttk.LabelFrame(main_frame, text=" Resultados ", padding=15)
        result_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Información del empleado
        ttk.Label(result_frame, text="Información del Empleado", style="Title.TLabel").pack(anchor='w')
        
        self.empleado_planilla_info = tk.Text(result_frame, height=4, wrap='word', font=('Arial', 9))
        self.empleado_planilla_info.pack(fill='x', pady=5)
        self.empleado_planilla_info.config(state='disabled')
        
        ttk.Separator(result_frame).pack(fill='x', pady=5)
        
        # Desglose de pago
        ttk.Label(result_frame, text="Desglose de Pago", style="Title.TLabel").pack(anchor='w')
        
        details_frame = ttk.Frame(result_frame)
        details_frame.pack(fill='x', pady=5)
        
        ttk.Label(details_frame, text="Sueldo Base:").grid(row=0, column=0, sticky='e', padx=5)
        self.sueldo_base_var = tk.StringVar(value="Q0.00")
        ttk.Label(details_frame, textvariable=self.sueldo_base_var).grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(details_frame, text="Horas Extras:").grid(row=1, column=0, sticky='e', padx=5)
        self.horas_extras_total_var = tk.StringVar(value="Q0.00")
        ttk.Label(details_frame, textvariable=self.horas_extras_total_var).grid(row=1, column=1, sticky='w', padx=5)
        
        ttk.Label(details_frame, text="Bono:").grid(row=2, column=0, sticky='e', padx=5)
        self.bono_total_var = tk.StringVar(value="Q0.00")
        ttk.Label(details_frame, textvariable=self.bono_total_var).grid(row=2, column=1, sticky='w', padx=5)
        
        ttk.Label(details_frame, text="Comisión:").grid(row=3, column=0, sticky='e', padx=5)
        self.comision_total_var = tk.StringVar(value="Q0.00")
        ttk.Label(details_frame, textvariable=self.comision_total_var).grid(row=3, column=1, sticky='w', padx=5)
        
        ttk.Separator(result_frame).pack(fill='x', pady=5)
        
        # Totales
        ttk.Label(result_frame, text="Total Ingresos:", style="Important.TLabel").pack(anchor='e')
        self.ingresos_var = tk.StringVar(value="Q0.00")
        ttk.Label(result_frame, textvariable=self.ingresos_var, font=('Arial', 10, 'bold')).pack(anchor='e')
        
        ttk.Label(result_frame, text="Total Deducciones:", style="Important.TLabel").pack(anchor='e')
        self.deducciones_var = tk.StringVar(value="Q0.00")
        ttk.Label(result_frame, textvariable=self.deducciones_var, font=('Arial', 10, 'bold')).pack(anchor='e')
        
        ttk.Separator(result_frame).pack(fill='x', pady=5)
        
        ttk.Label(result_frame, text="Total a Pagar:", style="Important.TLabel").pack(anchor='e')
        self.total_var = tk.StringVar(value="Q0.00")
        ttk.Label(result_frame, textvariable=self.total_var, font=('Arial', 12, 'bold')).pack(anchor='e')
        
        # Botón para imprimir/generar PDF
        ttk.Button(result_frame, text="🖨️ Generar Recibo", 
                  command=self.generar_recibo).pack(pady=10, ipadx=20)
    
    def buscar_para_planilla(self):
        codigo = self.codigo_planilla_var.get().strip()
        if not codigo:
            messagebox.showerror("Error", "Ingrese un código de empleado")
            return
        
        empleado = self.contratados.get(codigo)
        if not empleado:
            messagebox.showerror("Error", "Empleado no encontrado o no está contratado")
            return
        
        self.empleado_planilla = empleado
        
        # Mostrar información del empleado
        self.empleado_planilla_info.config(state='normal')
        self.empleado_planilla_info.delete(1.0, tk.END)
        
        info_text = f"""Código: {empleado['codigo']}
Nombre: {empleado['nombre']}
Área: {empleado['area']}
Sueldo Base: Q{empleado.get('sueldo_base', 0):.2f}
Jornada: {empleado.get('jornada', 'N/A')}
"""
        self.empleado_planilla_info.insert(tk.END, info_text)
        self.empleado_planilla_info.config(state='disabled')
        
        self.actualizar_status(f"Empleado encontrado: {empleado['nombre']}")
    
    def calcular_planilla(self):
        if not hasattr(self, 'empleado_planilla'):
            messagebox.showerror("Error", "Primero busque un empleado contratado")
            return
        
        try:
            horas_extras = int(self.horas_extras_var.get())
            bono = float(self.bono_var.get())
            adelantos = float(self.adelantos_var.get())
            prestamos = float(self.prestamos_var.get())
            sanciones = float(self.sanciones_var.get())
            
            if any(val < 0 for val in [horas_extras, bono, adelantos, prestamos, sanciones]):
                raise ValueError("Todos los valores deben ser positivos")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
            return
        
        # Cálculos
        sueldo_base = self.empleado_planilla['sueldo_base']
        valor_hora_extra = (sueldo_base / 160) * 1.5  # Suponiendo 160 horas/mes
        comision = self.empleado_planilla.get('comision', 0)
        
        total_horas_extras = horas_extras * valor_hora_extra
        total_comision = sueldo_base * (comision / 100)
        ingresos = sueldo_base + total_horas_extras + bono + total_comision
        deducciones = adelantos + prestamos + sanciones
        total = ingresos - deducciones
        
        # Mostrar resultados
        self.sueldo_base_var.set(f"Q{sueldo_base:.2f}")
        self.horas_extras_total_var.set(f"Q{total_horas_extras:.2f}")
        self.bono_total_var.set(f"Q{bono:.2f}")
        self.comision_total_var.set(f"Q{total_comision:.2f}")
        self.ingresos_var.set(f"Q{ingresos:.2f}")
        self.deducciones_var.set(f"Q{deducciones:.2f}")
        self.total_var.set(f"Q{total:.2f}")
        
        # Guardar historial de planilla
        if 'historial_planilla' not in self.empleado_planilla:
            self.empleado_planilla['historial_planilla'] = []
        
        self.empleado_planilla['historial_planilla'].append({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "ingresos": ingresos,
            "deducciones": deducciones,
            "total": total,
            "horas_extras": horas_extras,
            "bono": bono,
            "adelantos": adelantos,
            "prestamos": prestamos,
            "sanciones": sanciones
        
        
        })
        
        self.guardar_datos()
        self.actualizar_status(f"Planilla calculada para {self.empleado_planilla['nombre']}")
        
    
    def generar_recibo(self):
        if not hasattr(self, 'empleado_planilla'):
            messagebox.showerror("Error", "Primero calcule una planilla")
            return
        
        # En una implementación real, aquí generaría un PDF con el recibo
        messagebox.showinfo("Generar Recibo", "Función para generar PDF del recibo será implementada aquí")
    
    # --------------------------------------------
    # Funciones auxiliares
    # --------------------------------------------
    def generar_codigo(self, area_code):
        """Genera un código único para el empleado"""
        contador = 1
        for emp_id in self.empleados.keys():
            if emp_id.startswith(area_code):
                contador += 1
        return f"{area_code}{contador:03d}"
    
    def cerrar_ventana(self):
        """Maneja el cierre de la ventana"""
        self.guardar_datos()
        self.window.destroy()
        if not self.root:  # Si es la ventana principal
            try:
                self.root.quit()
            except:
                pass
    
    def run(self):
        self.window.mainloop()

def iniciar_modulo_rrhh(root=None):
    # Verificar si ya está abierto
    for widget in root.winfo_children() if root else []:
        if isinstance(widget, tk.Toplevel) and widget.title() == "Recursos Humanos - Textiles Rosy":
            widget.lift()
            return None
    app = RecursosHumanos(root)
    return app

if __name__ == "__main__":
    app = RecursosHumanos()
    app.run()