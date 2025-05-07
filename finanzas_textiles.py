import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from tkinter import filedialog
import uuid
from decimal import Decimal, getcontext
from tkcalendar import DateEntry

class FinanzasTextiles:
    def __init__(self, root=None, ventas=None, inventario=None, rrhh=None):
        self.root = root
        self.window = tk.Toplevel(root) if root else tk.Tk()
        self.window.title("Sistema Financiero - Textiles Rosy")
        self.window.geometry("1200x800")
        
        # Configuración de precisión decimal
        getcontext().prec = 6
        
        # Conexión con otros módulos
        self.modulo_ventas = ventas
        self.modulo_inventario = inventario
        self.modulo_rrhh = rrhh
        
        # Configuración contable
        self.cuentas_contables = self._cargar_catalogo_cuentas()
        self.tasa_iva = Decimal('0.12')  # 12% IVA Guatemala
        
        # Configuración de archivos
        self.data_dir = "data_finanzas"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.asientos_file = os.path.join(self.data_dir, "libro_diario.json")
        self.mayor_file = os.path.join(self.data_dir, "libro_mayor.json")
        self.iva_file = os.path.join(self.data_dir, "registro_iva.json")
        
        # Cargar datos
        self.libro_diario = self._cargar_datos(self.asientos_file, [])
        self.libro_mayor = self._cargar_datos(self.mayor_file, {})
        self.registro_iva = self._cargar_datos(self.iva_file, {"compras": [], "ventas": []})
        
        # Configurar interfaz
        self.conf_estilo()
        self.conf_gui()
        self.actualizar_saldos()
        
        # Control de cierre
        self.window.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
    
    def cerrar_ventana(self):
        """Maneja el cierre de la ventana"""
        self.guardar_datos()
        self.window.destroy()
    
    def _cargar_catalogo_cuentas(self):
        """Catálogo de cuentas según requisitos SAT Guatemala"""
        return {
            "1": {"nombre": "ACTIVOS", "subcuentas": {
                "1101": {"nombre": "Caja", "tipo": "debito"},
                "1105": {"nombre": "Bancos", "tipo": "debito"},
                "1201": {"nombre": "Inventario", "tipo": "debito"}
            }},
            "2": {"nombre": "PASIVOS", "subcuentas": {
                "2101": {"nombre": "Proveedores", "tipo": "credito"},
                "2105": {"nombre": "IVA por pagar", "tipo": "credito"},
                "2201": {"nombre": "Nóminas por pagar", "tipo": "credito"}
            }},
            "3": {"nombre": "PATRIMONIO", "subcuentas": {
                "3101": {"nombre": "Capital social", "tipo": "credito"}
            }},
            "4": {"nombre": "INGRESOS", "subcuentas": {
                "4101": {"nombre": "Ventas", "tipo": "credito"}
            }},
            "5": {"nombre": "GASTOS", "subcuentas": {
                "5101": {"nombre": "Costos de ventas", "tipo": "debito"},
                "5201": {"nombre": "Salarios", "tipo": "debito"},
                "5205": {"nombre": "IGSS", "tipo": "debito"},
                "5210": {"nombre": "ISR", "tipo": "debito"}
            }}
        }
    
    def _cargar_datos(self, archivo, default):
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r') as f:
                    data = json.load(f)
                    # Convertir strings a Decimal para los valores numéricos
                    if isinstance(data, list):
                        for item in data:
                            if 'movimientos' in item:
                                for mov in item['movimientos']:
                                    mov['debe'] = Decimal(mov['debe']) if isinstance(mov['debe'], str) else Decimal(str(mov['debe']))
                                    mov['haber'] = Decimal(mov['haber']) if isinstance(mov['haber'], str) else Decimal(str(mov['haber']))
                    elif isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, dict) and 'debe' in value and 'haber' in value and 'saldo' in value:
                                data[key] = {
                                    'debe': Decimal(value['debe']) if isinstance(value['debe'], str) else Decimal(str(value['debe'])),
                                    'haber': Decimal(value['haber']) if isinstance(value['haber'], str) else Decimal(str(value['haber'])),
                                    'saldo': Decimal(value['saldo']) if isinstance(value['saldo'], str) else Decimal(str(value['saldo']))
                                }
                    return data
            except Exception as e:
                print(f"Error cargando {archivo}: {str(e)}")
                return default
        return default
    
    def guardar_datos(self):
        """Guarda todos los registros contables"""
        with open(self.asientos_file, 'w') as f:
            json.dump(self.libro_diario, f, indent=4, cls=DecimalEncoder)
        with open(self.mayor_file, 'w') as f:
            json.dump(self.libro_mayor, f, indent=4, cls=DecimalEncoder)
        with open(self.iva_file, 'w') as f:
            json.dump(self.registro_iva, f, indent=4, cls=DecimalEncoder)
    
    def conf_estilo(self):
        """Estilo profesional para la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        PRIMARY_COLOR = "#3498db"
        SECONDARY_COLOR = "#2c3e50"
        BG_COLOR = "#f5f6fa"
        
        style.configure(".", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TButton", background=PRIMARY_COLOR, foreground="white", padding=5)
        style.configure("Treeview", fieldbackground="white", background="white")
        style.configure("Treeview.Heading", background=PRIMARY_COLOR, foreground="white")
        style.configure("TNotebook", background=BG_COLOR)
        style.configure("TNotebook.Tab", background="#bdc3c7", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", PRIMARY_COLOR)], foreground=[("selected", "white")])
    
    def conf_gui(self):
        """Interfaz principal con pestañas contables"""
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill='both')
        
        # Pestañas principales
        self.tab_diario = ttk.Frame(self.notebook)
        self.tab_mayor = ttk.Frame(self.notebook)
        self.tab_iva = ttk.Frame(self.notebook)
        self.tab_balance = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_diario, text="📒 Libro Diario")
        self.notebook.add(self.tab_mayor, text="📊 Libro Mayor")
        self.notebook.add(self.tab_iva, text="🧾 Registro IVA")
        self.notebook.add(self.tab_balance, text="⚖️ Balance")
        
        # Configurar cada pestaña
        self.crear_tab_diario()
        self.crear_tab_mayor()
        self.crear_tab_iva()
        self.crear_tab_balance()
        
        # Barra de estado
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief='sunken')
        status_bar.pack(fill='x')
        self.actualizar_status("Sistema listo")
    
    def actualizar_status(self, mensaje):
        """Actualiza la barra de estado con información financiera clave"""
        total_ventas = Decimal('0')
        total_nominas = Decimal('0')
        
        if self.modulo_ventas and hasattr(self.modulo_ventas, 'ventas'):
            total_ventas = sum(Decimal(str(v['total'])) for v in self.modulo_ventas.ventas)
        
        if self.modulo_rrhh and hasattr(self.modulo_rrhh, 'contratados'):
            total_nominas = sum(Decimal(str(n['total'])) for n in self.modulo_rrhh.contratados.values())
        
        self.status_var.set(f"Estado: {mensaje} | Ventas: Q{total_ventas:.2f} | Nóminas: Q{total_nominas:.2f}")

    # --------------------------------------------
    # Pestaña: Libro Diario
    # --------------------------------------------
    def crear_tab_diario(self):
        """Configura la interfaz del libro diario"""
        frame = ttk.Frame(self.tab_diario)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Treeview para asientos contables
        columns = ("fecha", "comprobante", "cuenta", "debe", "haber", "concepto")
        self.tree_diario = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree_diario.heading(col, text=col.capitalize())
            self.tree_diario.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree_diario.yview)
        self.tree_diario.configure(yscrollcommand=scrollbar.set)
        
        self.tree_diario.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botones de acción
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Sincronizar Ventas", 
                 command=self.sincronizar_ventas).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Sincronizar Nóminas", 
                 command=self.sincronizar_nominas).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Nuevo Asiento Manual", 
                 command=self.nuevo_asiento_manual).pack(side='right', padx=5)
        
        # Cargar datos iniciales
        self.actualizar_tree_diario()
    
    def sincronizar_ventas(self):
        """Registra automáticamente las ventas en el libro diario"""
        if not self.modulo_ventas or not hasattr(self.modulo_ventas, 'ventas'):
            messagebox.showerror("Error", "Módulo de Ventas no conectado o sin datos")
            return
        
        ventas_registradas = 0
        
        for venta in self.modulo_ventas.ventas:
            # Verificar si la venta ya está registrada
            if any(asiento.get('origen') == f"venta_{venta['id']}" for asiento in self.libro_diario):
                continue
            
            try:
                total = Decimal(str(venta['total']))
                iva = total * self.tasa_iva / (Decimal('1') + self.tasa_iva)
                subtotal = total - iva
                
                # Asiento contable
                asiento_venta = {
                    "id": str(uuid.uuid4()),
                    "fecha": venta['fecha'],
                    "origen": f"venta_{venta['id']}",
                    "movimientos": [
                        {
                            "cuenta": "1101",  # Caja
                            "debe": str(total),
                            "haber": "0",
                            "concepto": f"Venta {venta['id']}"
                        },
                        {
                            "cuenta": "4101",  # Ventas
                            "debe": "0",
                            "haber": str(subtotal),
                            "concepto": "Venta de mercadería"
                        },
                        {
                            "cuenta": "2105",  # IVA por pagar
                            "debe": "0",
                            "haber": str(iva),
                            "concepto": "IVA ventas"
                        }
                    ]
                }
                
                self.libro_diario.append(asiento_venta)
                ventas_registradas += 1
                
                # Registrar en libro de IVA
                self.registro_iva["ventas"].append({
                    "fecha": venta['fecha'],
                    "nit": venta['cliente']['nit'],
                    "numero_factura": venta['id'],
                    "subtotal": str(subtotal),
                    "iva": str(iva),
                    "total": str(total)
                })
                
            except Exception as e:
                print(f"Error procesando venta {venta['id']}: {str(e)}")
                continue
        
        if ventas_registradas > 0:
            self.guardar_datos()
            self.actualizar_tree_diario()
            self.actualizar_mayor()
            messagebox.showinfo("Éxito", f"{ventas_registradas} ventas sincronizadas")
        else:
            messagebox.showinfo("Información", "No hay nuevas ventas para registrar")
    
    def sincronizar_nominas(self):
        """Registra las nóminas de RRHH en el libro diario"""
        if not self.modulo_rrhh or not hasattr(self.modulo_rrhh, 'contratados'):
            messagebox.showerror("Error", "Módulo de RRHH no conectado o sin datos")
            return
        
        nominas_registradas = 0
        
        for codigo, empleado in self.modulo_rrhh.contratados.items():
            if 'historial_planilla' not in empleado:
                continue
                
            for planilla in empleado['historial_planilla']:
                # Verificar si ya está registrada
                if any(asiento.get('origen') == f"planilla_{codigo}_{planilla['fecha']}" 
                     for asiento in self.libro_diario):
                    continue
                
                try:
                    total = Decimal(str(planilla['total']))
                    deducciones = Decimal(str(planilla.get('deducciones', 0)))
                    salario_neto = total - deducciones
                    
                    # Asiento contable
                    asiento_nomina = {
                        "id": str(uuid.uuid4()),
                        "fecha": planilla['fecha'],
                        "origen": f"planilla_{codigo}_{planilla['fecha']}",
                        "movimientos": [
                            {
                                "cuenta": "5201",  # Salarios
                                "debe": str(salario_neto),
                                "haber": "0",
                                "concepto": f"Pago a {empleado['nombre']}"
                            },
                            {
                                "cuenta": "5205",  # IGSS
                                "debe": str(planilla.get('igss', 0)),
                                "haber": "0",
                                "concepto": "Cuota patronal IGSS"
                            },
                            {
                                "cuenta": "5210",  # ISR
                                "debe": str(planilla.get('isr', 0)),
                                "haber": "0",
                                "concepto": "Retención ISR"
                            },
                            {
                                "cuenta": "1101",  # Caja
                                "debe": "0",
                                "haber": str(total),
                                "concepto": "Pago de nómina"
                            }
                        ]
                    }
                    
                    self.libro_diario.append(asiento_nomina)
                    nominas_registradas += 1
                    
                except Exception as e:
                    print(f"Error procesando nómina {codigo}: {str(e)}")
                    continue
        
        if nominas_registradas > 0:
            self.guardar_datos()
            self.actualizar_tree_diario()
            self.actualizar_mayor()
            messagebox.showinfo("Éxito", f"{nominas_registradas} nóminas sincronizadas")
        else:
            messagebox.showinfo("Información", "No hay nuevas nóminas para registrar")
    
    def actualizar_tree_diario(self):
        """Actualiza el Treeview con los asientos del libro diario"""
        for item in self.tree_diario.get_children():
            self.tree_diario.delete(item)
            
        for asiento in sorted(self.libro_diario, key=lambda x: x['fecha']):
            fecha = datetime.fromisoformat(asiento['fecha']).strftime('%d/%m/%Y')
            
            for mov in asiento['movimientos']:
                self.tree_diario.insert('', 'end', values=(
                    fecha,
                    asiento.get('origen', 'Manual'),
                    f"{mov['cuenta']} - {self.get_nombre_cuenta(mov['cuenta'])}",
                    f"Q{Decimal(mov['debe']):.2f}" if Decimal(mov['debe']) > 0 else "",
                    f"Q{Decimal(mov['haber']):.2f}" if Decimal(mov['haber']) > 0 else "",
                    mov['concepto']
                ))

    # --------------------------------------------
    # Pestaña: Libro Mayor
    # --------------------------------------------
    def crear_tab_mayor(self):
        """Configura la interfaz del libro mayor"""
        frame = ttk.Frame(self.tab_mayor)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Treeview para cuentas del mayor
        columns = ("cuenta", "debe", "haber", "saldo")
        self.tree_mayor = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree_mayor.heading(col, text=col.capitalize())
            self.tree_mayor.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree_mayor.yview)
        self.tree_mayor.configure(yscrollcommand=scrollbar.set)
        
        self.tree_mayor.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botón de actualización
        ttk.Button(frame, text="Actualizar Mayor", 
                 command=self.actualizar_mayor).pack(pady=5)
        
        # Cargar datos iniciales
        self.actualizar_mayor()
    
    def actualizar_mayor(self):
        """Actualiza el libro mayor a partir del diario"""
        self.libro_mayor = {}
        
        # Procesar todos los asientos
        for asiento in self.libro_diario:
            for mov in asiento['movimientos']:
                cuenta = mov['cuenta']
                debe = Decimal(mov['debe'])
                haber = Decimal(mov['haber'])
                
                if cuenta not in self.libro_mayor:
                    self.libro_mayor[cuenta] = {
                        "debe": Decimal('0'),
                        "haber": Decimal('0'),
                        "saldo": Decimal('0')
                    }
                
                self.libro_mayor[cuenta]["debe"] += debe
                self.libro_mayor[cuenta]["haber"] += haber
        
        # Calcular saldos
        for cuenta, datos in self.libro_mayor.items():
            tipo_cuenta = self.get_tipo_cuenta(cuenta)
            if tipo_cuenta == "debito":
                datos["saldo"] = datos["debe"] - datos["haber"]
            else:
                datos["saldo"] = datos["haber"] - datos["debe"]
        
        self.guardar_datos()
        self.actualizar_tree_mayor()
    
    def actualizar_tree_mayor(self):
        """Actualiza el Treeview con los datos del libro mayor"""
        for item in self.tree_mayor.get_children():
            self.tree_mayor.delete(item)
            
        for cuenta, datos in sorted(self.libro_mayor.items()):
            nombre = self.get_nombre_cuenta(cuenta)
            saldo = datos['saldo']
            
            # Solo mostrar cuentas con saldo diferente de cero
            if saldo != Decimal('0'):
                self.tree_mayor.insert('', 'end', values=(
                    f"{cuenta} - {nombre}",
                    f"Q{datos['debe']:.2f}",
                    f"Q{datos['haber']:.2f}",
                    f"Q{datos['saldo']:.2f}",
                ))

    # --------------------------------------------
    # Pestaña: Registro IVA
    # --------------------------------------------
    def crear_tab_iva(self):
        """Configura la interfaz del registro de IVA"""
        notebook = ttk.Notebook(self.tab_iva)
        notebook.pack(expand=True, fill='both')
        
        # Sub-pestañas para IVA Compras/Ventas
        tab_compras = ttk.Frame(notebook)
        tab_ventas = ttk.Frame(notebook)
        
        notebook.add(tab_compras, text="IVA Compras")
        notebook.add(tab_ventas, text="IVA Ventas")
        
        # Configurar Treeview para Compras
        columns = ("fecha", "nit", "numero", "subtotal", "iva", "total")
        self.tree_iva_compras = ttk.Treeview(tab_compras, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_iva_compras.heading(col, text=col.capitalize())
            self.tree_iva_compras.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tab_compras, orient='vertical', command=self.tree_iva_compras.yview)
        self.tree_iva_compras.configure(yscrollcommand=scrollbar.set)
        
        self.tree_iva_compras.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Configurar Treeview para Ventas
        self.tree_iva_ventas = ttk.Treeview(tab_ventas, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_iva_ventas.heading(col, text=col.capitalize())
            self.tree_iva_ventas.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tab_ventas, orient='vertical', command=self.tree_iva_ventas.yview)
        self.tree_iva_ventas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_iva_ventas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Cargar datos iniciales
        self.actualizar_tree_iva()
    
    def actualizar_tree_iva(self):
        """Actualiza los Treeview de IVA"""
        for item in self.tree_iva_compras.get_children():
            self.tree_iva_compras.delete(item)
            
        for item in self.tree_iva_ventas.get_children():
            self.tree_iva_ventas.delete(item)
            
        for registro in self.registro_iva["compras"]:
            self.tree_iva_compras.insert('', 'end', values=(
                datetime.fromisoformat(registro['fecha']).strftime('%d/%m/%Y'),
                registro['nit'],
                registro['numero_factura'],
                f"Q{Decimal(registro['subtotal']):.2f}",
                f"Q{Decimal(registro['iva']):.2f}",
                f"Q{Decimal(registro['total']):.2f}"
            ))
            
        for registro in self.registro_iva["ventas"]:
            self.tree_iva_ventas.insert('', 'end', values=(
                datetime.fromisoformat(registro['fecha']).strftime('%d/%m/%Y'),
                registro['nit'],
                registro['numero_factura'],
                f"Q{Decimal(registro['subtotal']):.2f}",
                f"Q{Decimal(registro['iva']):.2f}",
                f"Q{Decimal(registro['total']):.2f}"
            ))

    # --------------------------------------------
    # Pestaña: Balance General
    # --------------------------------------------
    def crear_tab_balance(self):
        """Configura la interfaz del balance general"""
        frame = ttk.Frame(self.tab_balance)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Treeview para el balance
        columns = ("cuenta", "saldo")
        self.tree_balance = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        self.tree_balance.heading("cuenta", text="Cuenta")
        self.tree_balance.heading("saldo", text="Saldo")
        
        self.tree_balance.column("cuenta", width=300)
        self.tree_balance.column("saldo", width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree_balance.yview)
        self.tree_balance.configure(yscrollcommand=scrollbar.set)
        
        self.tree_balance.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botón de actualización
        ttk.Button(frame, text="Generar Balance", 
                 command=self.generar_balance).pack(pady=5)
        
        # Cargar datos iniciales
        self.generar_balance()
    
    def generar_balance(self):
        """Genera el balance general agrupando cuentas"""
        for item in self.tree_balance.get_children():
            self.tree_balance.delete(item)
            
        # Agrupar por categorías
        categorias = {
            "ACTIVOS": Decimal('0'),
            "PASIVOS": Decimal('0'),
            "PATRIMONIO": Decimal('0'),
            "RESULTADOS": Decimal('0')
        }
        
        # Calcular totales por categoría
        for cuenta, datos in self.libro_mayor.items():
            grupo = self.get_grupo_cuenta(cuenta)
            if grupo in categorias:
                categorias[grupo] += datos['saldo']
        
        # Insertar en Treeview
        for grupo, total in categorias.items():
            self.tree_balance.insert('', 'end', values=(grupo, f"Q{total:.2f}"), tags=('grupo',))
            
            # Insertar cuentas detalladas
            for cuenta, datos in self.libro_mayor.items():
                if self.get_grupo_cuenta(cuenta) == grupo and abs(datos['saldo']) > Decimal('0.01'):
                    nombre = self.get_nombre_cuenta(cuenta)
                    self.tree_balance.insert('', 'end', values=(
                        f"   {cuenta} - {nombre}",
                        f"Q{datos['saldo']:.2f}"
                    ))
        
        # Configurar estilo para grupos
        self.tree_balance.tag_configure('grupo', font=('Arial', 10, 'bold'))

    # --------------------------------------------
    # Funciones auxiliares
    # --------------------------------------------
    def get_nombre_cuenta(self, codigo):
        """Obtiene el nombre de una cuenta contable"""
        for grupo in self.cuentas_contables.values():
            if codigo in grupo['subcuentas']:
                return grupo['subcuentas'][codigo]['nombre']
        return "Cuenta no definida"
    
    def get_tipo_cuenta(self, codigo):
        """Obtiene el tipo de una cuenta (debito/credito)"""
        for grupo in self.cuentas_contables.values():
            if codigo in grupo['subcuentas']:
                return grupo['subcuentas'][codigo]['tipo']
        return "debito"
    
    def get_grupo_cuenta(self, codigo):
        """Obtiene el grupo principal de una cuenta"""
        for grupo_id, grupo in self.cuentas_contables.items():
            if codigo in grupo['subcuentas']:
                return grupo['nombre']
        return "OTROS"
    
    def nuevo_asiento_manual(self):
        """Permite crear un asiento contable manualmente"""
        def guardar_asiento():
            try:
                fecha = fecha_entry.get_date().isoformat()
                cuenta_debito = debito_cb.get().split(" - ")[0]
                cuenta_credito = credito_cb.get().split(" - ")[0]
                monto = Decimal(monto_entry.get())
                concepto = concepto_entry.get()
                
                if not cuenta_debito or not cuenta_credito or monto <= 0:
                    raise ValueError("Datos inválidos")
                    
                # Verificar que las cuentas existan
                if not any(cuenta_debito in grupo['subcuentas'] for grupo in self.cuentas_contables.values()):
                    raise ValueError(f"Cuenta débito {cuenta_debito} no existe")
                    
                if not any(cuenta_credito in grupo['subcuentas'] for grupo in self.cuentas_contables.values()):
                    raise ValueError(f"Cuenta crédito {cuenta_credito} no existe")
                
                asiento = {
                    "id": str(uuid.uuid4()),
                    "fecha": fecha,
                    "origen": "manual",
                    "movimientos": [
                        {
                            "cuenta": cuenta_debito,
                            "debe": str(monto),
                            "haber": "0",
                            "concepto": concepto
                        },
                        {
                            "cuenta": cuenta_credito,
                            "debe": "0",
                            "haber": str(monto),
                            "concepto": concepto
                        }
                    ]
                }
                
                self.libro_diario.append(asiento)
                self.guardar_datos()
                self.actualizar_tree_diario()
                self.actualizar_mayor()
                top.destroy()
                messagebox.showinfo("Éxito", "Asiento contable registrado")
                
            except Exception as e:
                messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        
        top = tk.Toplevel(self.window)
        top.title("Nuevo Asiento Contable")
        top.geometry("400x300")
        
        ttk.Label(top, text="Fecha:").grid(row=0, column=0, padx=5, pady=5)
        fecha_entry = DateEntry(top, date_pattern='yyyy-mm-dd')
        fecha_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Cuenta Débito:").grid(row=1, column=0, padx=5, pady=5)
        debito_cb = ttk.Combobox(top, values=self.get_lista_cuentas(), state='readonly')
        debito_cb.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Cuenta Crédito:").grid(row=2, column=0, padx=5, pady=5)
        credito_cb = ttk.Combobox(top, values=self.get_lista_cuentas(), state='readonly')
        credito_cb.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Monto (Q):").grid(row=3, column=0, padx=5, pady=5)
        monto_entry = ttk.Entry(top)
        monto_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Concepto:").grid(row=4, column=0, padx=5, pady=5)
        concepto_entry = ttk.Entry(top)
        concepto_entry.grid(row=4, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(top)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Guardar", command=guardar_asiento).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=top.destroy).pack(side='right', padx=5)
    
    def get_lista_cuentas(self):
        """Genera lista de cuentas para Combobox"""
        cuentas = []
        for grupo in self.cuentas_contables.values():
            for codigo, detalle in grupo['subcuentas'].items():
                cuentas.append(f"{codigo} - {detalle['nombre']}")
        return sorted(cuentas)
    
    def actualizar_saldos(self):
        """Actualiza todos los saldos y registros"""
        self.actualizar_mayor()
        self.actualizar_tree_diario()
        self.actualizar_tree_iva()
        self.generar_balance()
    
    def run(self):
        """Inicia la aplicación"""
        self.window.mainloop()

class DecimalEncoder(json.JSONEncoder):
    """Helper para serializar Decimal a JSON"""
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)

def iniciar_modulo_finanzas(root=None, ventas=None, inventario=None, rrhh=None):
    # Verificar si ya está abierto
    for widget in root.winfo_children() if root else []:
        if isinstance(widget, tk.Toplevel) and widget.title() == "Sistema Financiero - Textiles Rosy":
            widget.lift()
            return None
    app = FinanzasTextiles(root, ventas, inventario, rrhh)
    return app

if __name__ == "__main__":
    app = FinanzasTextiles()
    app.run()