import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import time
from datetime import datetime
import threading
import tkcalendar
import json
import os
import uuid

class ProductoTextil:
    def __init__(self, tipo, cantidad=1, stock=0):
        self.tipo = tipo
        self.cantidad = cantidad
        self.stock = stock
    
    def calcular_subtotal(self, precios_productos):
        return precios_productos[self.tipo] * self.cantidad
    
    def __str__(self):
        return f"{self.cantidad}x {self.tipo} (Stock: {self.stock})"

class Cliente:
    def __init__(self, nombre="", nit="", metodo_pago="Efectivo"):
        self.nombre = nombre
        self.nit = nit
        self.metodo_pago = metodo_pago

class Ticket:
    def __init__(self, orden_id, productos, total, cliente, timestamp=None):
        self.ticket_id = str(uuid.uuid4())[:8].upper()
        self.orden_id = orden_id
        self.productos = productos
        self.total = total
        self.cliente = cliente
        self.timestamp = timestamp or datetime.now()
        self.establecimiento = "Textiles Rosy"
        self.direccion = "Dirección de la empresa"
        self.ciudad = "Ciudad, País"
        self.telefono = "Teléfono de contacto"
        self.redes_sociales = {
            "Facebook": "TextilesRosy",
            "Instagram": "@textiles_rosy",
            "Twitter": "@textiles_rosy"
        }

    def to_dict(self):
        return {
            'ticket_id': self.ticket_id,
            'orden_id': self.orden_id,
            'productos': [(p.tipo, p.cantidad) for p in self.productos],
            'total': self.total,
            'cliente': {
                'nombre': self.cliente.nombre,
                'nit': self.cliente.nit,
                'metodo_pago': self.cliente.metodo_pago
            },
            'timestamp': self.timestamp.isoformat(),
            'establecimiento': self.establecimiento,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'telefono': self.telefono,
            'redes_sociales': self.redes_sociales
        }

    @classmethod
    def from_dict(cls, data):
        cliente_data = data.get('cliente', {})
        cliente = Cliente(
            cliente_data.get('nombre', ''),
            cliente_data.get('nit', ''),
            cliente_data.get('metodo_pago', 'Efectivo')
        )
        
        ticket = cls(
            data['orden_id'],
            [ProductoTextil(tipo, cantidad) for tipo, cantidad in data['productos']],
            data['total'],
            cliente,
            datetime.fromisoformat(data['timestamp'])
        )
        ticket.ticket_id = data['ticket_id']
        ticket.establecimiento = data['establecimiento']
        ticket.direccion = data.get('direccion', ticket.direccion)
        ticket.ciudad = data.get('ciudad', ticket.ciudad)
        ticket.telefono = data.get('telefono', ticket.telefono)
        ticket.redes_sociales = data.get('redes_sociales', ticket.redes_sociales)
        return ticket

class SistemaPedidosTextiles:
    def __init__(self, root=None):
        self.window = tk.Toplevel(root) if root else tk.Tk()
        self.window.title("Sistema de Pedidos - Textiles Rosy")
        self.window.geometry("1200x800")
        
        # Sistema de tickets y stock
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.tickets_file = os.path.join(self.data_dir, "tickets.json")
        self.stock_file = os.path.join(self.data_dir, "stock.json")
        
        self.tickets = self.cargar_tickets()
        self.precio_productos, self.stock_productos = self.cargar_stock()
        
        self.conf_estilo()
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Variables
        self.contador_orden = 1
        self.ordenes_activas = {}
        self.productos_en_carrito = []
        self.cliente_actual = Cliente()
        
        # Variables de interfaz
        self.preparing_canvas = None
        self.completed_canvas = None
        self.preparing_frame = None
        self.completed_frame = None
        self.tickets_canvas = None
        self.tickets_lista_frame = None
        self.tickets_list = None
        
        self.conf_menu()
        self.conf_gui()
        self.conf_precio_menu()
        self.setup_info_panel()
        
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def cargar_tickets(self):
        if os.path.exists(self.tickets_file):
            try:
                with open(self.tickets_file, 'r') as f:
                    data = json.load(f)
                    return [Ticket.from_dict(t) for t in data]
            except Exception as e:
                print(f"Error al cargar tickets: {e}")
                return []
        return []

    def cargar_stock(self):
        precios = {
            # Guipiles
            "Petzal Computarizado": 90,
            "Petzal Alfombra": 800,
            "Petzal Corona": 750,
            "San Pedro": 340,
            "San Lucas": 240,
            "Mariposa Computarizada": 90,
            "Canasta Computarizada": 100,
            "San Pedro Mariposa": 250,
            "Guipil de Toto": 350,
            # Cortes
            "Fino hilo alemán": 1500,
            "Fino hilo cristal": 2000,
            "De toto": 750,
            "Rojo alemán": 1200,
            # Fajas
            "Computarizada de 3 dedos": 50,
            "Computarizada de 4 dedos": 55,
            "Computarizada de 6 dedos": 80,
            "Marcador sencillo": 300,
            "Marcador fino": 1200,
        }
        
        stock = {producto: 0 for producto in precios.keys()}
        
        if os.path.exists(self.stock_file):
            try:
                with open(self.stock_file, 'r') as f:
                    stock.update(json.load(f))
            except Exception as e:
                print(f"Error al cargar stock: {e}")
        
        return precios, stock

    def guardar_datos(self):
        try:
            # Guardar tickets
            with open(self.tickets_file, 'w') as f:
                json.dump([t.to_dict() for t in self.tickets], f, indent=4)
            
            # Guardar stock
            with open(self.stock_file, 'w') as f:
                json.dump(self.stock_productos, f, indent=4)
        except Exception as e:
            print(f"Error al guardar datos: {e}")

    def generar_ticket(self, orden_id, productos, total, cliente):
        # Actualizar stock
        for producto in productos:
            if producto.tipo in self.stock_productos:
                self.stock_productos[producto.tipo] -= producto.cantidad
                if self.stock_productos[producto.tipo] < 0:
                    self.stock_productos[producto.tipo] = 0
        
        ticket = Ticket(orden_id, productos, total, cliente)
        self.tickets.append(ticket)
        self.guardar_datos()
        return ticket

    def conf_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores principales
        PRIMARY_COLOR = "#4a90e2"
        SECONDARY_COLOR = "#2c3e50"
        BG_COLOR = "#f5f6fa"
        ACCENT_COLOR = "#2ecc71"
        WARNING_COLOR = "#e74c3c"
        
        # Configurar estilos generales
        style.configure(".",
                    background=BG_COLOR,
                    foreground=SECONDARY_COLOR,
                    font=('Segoe UI', 9))
        
        # Notebook
        style.configure("TNotebook",
                    background=BG_COLOR,
                    tabmargins=[2, 5, 2, 0])
        
        style.configure("TNotebook.Tab",
                    background=BG_COLOR,
                    foreground=SECONDARY_COLOR,
                    padding=[10, 5],
                    font=('Segoe UI', 9, 'bold'))
        
        style.map("TNotebook.Tab",
                background=[("selected", PRIMARY_COLOR)],
                foreground=[("selected", "white")])
        
        # Frames y otros estilos
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabelframe", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TLabelframe.Label", background=BG_COLOR, foreground=SECONDARY_COLOR,
                    font=('Segoe UI', 9, 'bold'))
        
        # Botones
        style.configure("TButton", background=PRIMARY_COLOR, foreground="white",
                    padding=[10, 5], font=('Segoe UI', 9, 'bold'))
        style.map("TButton",
                background=[("active", SECONDARY_COLOR)],
                foreground=[("active", "white")])
        
        # Botón de advertencia
        style.configure("Warning.TButton", background=WARNING_COLOR, foreground="white",
                    padding=[10, 5], font=('Segoe UI', 9, 'bold'))
        style.map("Warning.TButton",
                background=[("active", "#c0392b")],
                foreground=[("active", "white")])
        
        # Botón de éxito
        style.configure("Success.TButton", background=ACCENT_COLOR, foreground="white",
                    padding=[10, 5], font=('Segoe UI', 9, 'bold'))
        style.map("Success.TButton",
                background=[("active", "#27ae60")],
                foreground=[("active", " white")])
        
        # Estilos para tickets
        style.configure("Ticket.TFrame", background="white")
        style.configure("Ticket.TLabel",
                    background="white",
                    font=('Segoe UI', 9))
        style.configure("TicketHeader.TLabel",
                    background="white",
                    font=('Segoe UI', 12, 'bold'))
        style.configure("TicketTitle.TLabel",
                    background="white",
                    font=('Segoe UI', 14, 'bold'))
        style.configure("TicketTotal.TLabel",
                    background="white",
                    font=('Segoe UI', 11, 'bold'))
        
        # Otros widgets
        style.configure("TLabel", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TCombobox", selectbackground=PRIMARY_COLOR,
                    selectforeground="white", fieldbackground="white")
        style.configure("TCheckbutton", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TProgressbar", troughcolor=BG_COLOR, background=ACCENT_COLOR)
        
        # Etiquetas especiales
        style.configure("Header.TLabel", font=('Segoe UI', 10, 'bold'),
                    foreground=SECONDARY_COLOR, background=BG_COLOR)
        style.configure("Title.TLabel", font=('Segoe UI', 20, 'bold'),
                    foreground=PRIMARY_COLOR, background=BG_COLOR)
        style.configure("Subtitle.TLabel", font=('Segoe UI', 12, 'bold'),
                    foreground=SECONDARY_COLOR, background=BG_COLOR)
        
        # Menú
        style.configure("Bold.TLabelframe.Label", font=('Segoe UI', 12, 'bold'),
                    foreground=PRIMARY_COLOR, background=BG_COLOR)
        
        self.window.configure(bg=BG_COLOR)

    def conf_menu(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar Tickets", command=self.exportar_tickets)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.salir)
        
        tickets_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tickets", menu=tickets_menu)
        tickets_menu.add_command(label="Buscar Ticket", command=self.buscar_ticket)
        tickets_menu.add_command(label="Ver Historial", command=lambda: self.notebook.select(2))
        
        stock_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Inventario", menu=stock_menu)
        stock_menu.add_command(label="Administrar Stock", command=self.mostrar_stock)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="¿Cómo funciona?", command=self.mostrar_ayuda)
        help_menu.add_command(label="Créditos", command=self.mostrar_creditos)

    def conf_gui(self):
        self.notebook = ttk.Notebook(self.window)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.new_order_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.new_order_frame, text="Nuevo Pedido")
        self.conf_nueva_orden_tab()

        self.ordenes_activas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ordenes_activas_frame, text="Pedidos Activos")
        self.setup_ordenes_activas_tab()
        
        self.tickets_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tickets_frame, text="Historial de Tickets")
        self.conf_tickets_tab()
        
        self.stock_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stock_frame, text="Inventario", state='hidden')

    def conf_tickets_tab(self):
        self.tickets_frame.grid_columnconfigure(0, weight=1)
        self.tickets_frame.grid_rowconfigure(1, weight=1)
        
        # Panel superior con controles
        control_frame = ttk.Frame(self.tickets_frame)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Filtros de búsqueda
        ttk.Label(control_frame, text="Fecha:").pack(side="left", padx=5)
        
        # Configuración del calendario
        self.fecha_filtro = tkcalendar.DateEntry(
            control_frame,
            width=12,
            background='royal blue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            state='readonly',
            locale='es_MX',
            showweeknumbers=False,
            firstweekday='monday'
        )
        self.fecha_filtro.pack(side="left", padx=5)

        self.fecha_filtro.bind('<<DateEntrySelected>>', lambda e: self.after_date_selection())
        
        ttk.Label(control_frame, text="Buscar:").pack(side="left", padx=5)
        self.busqueda_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.busqueda_var, width=20).pack(
            side="left", padx=5)
        
        ttk.Button(control_frame, text="Buscar", 
                command=self.filtrar_tickets).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Limpiar Filtros", 
                command=self.limpiar_filtros).pack(side="left", padx=5)
        
        # Lista de tickets con scroll
        self.tickets_list = ttk.Treeview(self.tickets_frame, 
            columns=("fecha", "total", "estado", "items"),
            show="headings",
            height=15)
        
        # Configuracion de columnas
        self.tickets_list.heading("fecha", text="Fecha y Hora")
        self.tickets_list.heading("total", text="Total")
        self.tickets_list.heading("estado", text="Ticket ID")
        self.tickets_list.heading("items", text="Items")
        
        self.tickets_list.column("fecha", width=150)
        self.tickets_list.column("total", width=100)
        self.tickets_list.column("estado", width=100)
        self.tickets_list.column("items", width=400)
        
        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(self.tickets_frame, orient="vertical", 
                                command=self.tickets_list.yview)
        self.tickets_list.configure(yscrollcommand=scrollbar.set)
        
        self.tickets_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Botón para ver detalle
        ttk.Button(self.tickets_frame, text="Ver Detalle", 
                command=self.ver_ticket_seleccionado).grid(
            row=2, column=0, pady=5)
        
        # Cargar tickets iniciales
        self.actualizar_lista_tickets()
        
        # Bind doble click
        self.tickets_list.bind("<Double-1>", lambda e: self.ver_ticket_seleccionado())

    def after_date_selection(self):
        try:
            self.filtrar_tickets()
        except Exception as e:
            print(f"Error al filtrar tickets: {e}")

    def limpiar_filtros(self):
        try:
            self.fecha_filtro.set_date(datetime.now())
            self.busqueda_var.set("")
            self.actualizar_lista_tickets()
        except Exception as e:
            print(f"Error al limpiar filtros: {e}")

    def filtrar_tickets(self):
        try:
            fecha = self.fecha_filtro.get_date()
            busqueda = self.busqueda_var.get().lower()
            
            tickets_filtrados = [
                t for t in self.tickets
                if (t.timestamp.date() == fecha and
                    (not busqueda or
                    busqueda in t.ticket_id.lower() or
                    busqueda in str(t.total).lower() or
                    any(busqueda in str(b).lower() for b in t.productos)))
            ]
            
            self.actualizar_lista_tickets(tickets_filtrados)
        except Exception as e:
            print(f"Error al filtrar tickets: {e}")
            self.actualizar_lista_tickets()

    def actualizar_lista_tickets(self, tickets_filtrados=None):
        # Limpiar lista actual
        for item in self.tickets_list.get_children():
            self.tickets_list.delete(item)
        
        # Mostrar tickets
        tickets_a_mostrar = tickets_filtrados if tickets_filtrados is not None else self.tickets
        for ticket in reversed(tickets_a_mostrar):
            self.tickets_list.insert("", "end", values=(
                ticket.timestamp.strftime('%d/%m/%Y %H:%M'),
                f"Q{ticket.total:.2f}",
                ticket.ticket_id,
                ", ".join(str(b) for b in ticket.productos)
            ))

    def ver_ticket_seleccionado(self):
        seleccion = self.tickets_list.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un ticket")
            return
        
        ticket_id = self.tickets_list.item(seleccion[0])['values'][2]
        ticket = next((t for t in self.tickets if t.ticket_id == ticket_id), None)
        
        if ticket:
            self.mostrar_detalle_ticket(ticket)

    def mostrar_stock(self):
        self.notebook.tab(3, state='normal')
        self.notebook.select(3)
        self.conf_stock_tab()

    def conf_stock_tab(self):
        for widget in self.stock_frame.winfo_children():
            widget.destroy()
            
        self.stock_frame.grid_columnconfigure(0, weight=1)
        self.stock_frame.grid_rowconfigure(1, weight=1)
        
        # Frame de controles
        control_frame = ttk.Frame(self.stock_frame)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Label(control_frame, text="Producto:").pack(side="left", padx=5)
        self.stock_producto_var = tk.StringVar()
        product_combo = ttk.Combobox(control_frame, 
                                   textvariable=self.stock_producto_var,
                                   values=list(self.precio_productos.keys()),
                                   state="readonly")
        product_combo.pack(side="left", padx=5)
        
        ttk.Label(control_frame, text="Cantidad:").pack(side="left", padx=5)
        self.stock_cantidad_var = tk.IntVar(value=0)
        ttk.Spinbox(control_frame, from_=0, to=1000, 
                   textvariable=self.stock_cantidad_var).pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="Actualizar Stock", 
                  command=self.actualizar_stock).pack(side="left", padx=5)
        
        # Lista de stock
        columns = ("producto", "precio", "stock")
        self.stock_tree = ttk.Treeview(self.stock_frame, columns=columns, show="headings")
        self.stock_tree.heading("producto", text="Producto")
        self.stock_tree.heading("precio", text="Precio (Q)")
        self.stock_tree.heading("stock", text="Stock")
        
        self.stock_tree.column("producto", width=300)
        self.stock_tree.column("precio", width=150, anchor='e')
        self.stock_tree.column("stock", width=150, anchor='e')
        
        scrollbar = ttk.Scrollbar(self.stock_frame, orient="vertical", 
                                command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stock_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Actualizar lista
        self.actualizar_lista_stock()
        
        # Botón para exportar stock
        ttk.Button(self.stock_frame, text="Exportar Stock", 
                  command=self.exportar_stock).grid(row=2, column=0, pady=5)

    def actualizar_lista_stock(self):
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
            
        for producto, precio in self.precio_productos.items():
            stock = self.stock_productos.get(producto, 0)
            self.stock_tree.insert("", "end", values=(
                producto,
                f"{precio:.2f}",
                stock
            ))

    def actualizar_stock(self):
        producto = self.stock_producto_var.get()
        cantidad = self.stock_cantidad_var.get()
        
        if not producto:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
            
        if cantidad < 0:
            messagebox.showwarning("Advertencia", "La cantidad no puede ser negativa")
            return
            
        self.stock_productos[producto] = cantidad
        self.guardar_datos()
        self.actualizar_lista_stock()
        messagebox.showinfo("Éxito", f"Stock de {producto} actualizado a {cantidad}")

    def exportar_stock(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        if filename:
            try:
                if filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Producto', 'Precio', 'Stock'])
                        for producto, precio in self.precio_productos.items():
                            stock = self.stock_productos.get(producto, 0)
                            writer.writerow([producto, precio, stock])
                else:
                    data = {
                        'precios': self.precio_productos,
                        'stock': self.stock_productos
                    }
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=4)
                messagebox.showinfo("Éxito", "Stock exportado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar stock: {str(e)}")

    def conf_nueva_orden_tab(self):
        self.new_order_frame.grid_columnconfigure(0, weight=1)
        self.new_order_frame.grid_rowconfigure(1, weight=1)
        
        # Variables
        self.drink_var = tk.StringVar()
        self.cantidad_var = tk.IntVar(value=1)
        
        # Panel de cliente
        cliente_frame = ttk.LabelFrame(self.new_order_frame, text="Datos del Cliente")
        cliente_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Label(cliente_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.cliente_nombre_var = tk.StringVar()
        ttk.Entry(cliente_frame, textvariable=self.cliente_nombre_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(cliente_frame, text="NIT:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.cliente_nit_var = tk.StringVar()
        ttk.Entry(cliente_frame, textvariable=self.cliente_nit_var).grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(cliente_frame, text="Método de Pago:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.cliente_pago_var = tk.StringVar(value="Efectivo")
        ttk.Combobox(cliente_frame, textvariable=self.cliente_pago_var,
                    values=["Efectivo", "Tarjeta", "Transferencia"]).grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Panel de pedido
        order_panel = ttk.LabelFrame(self.new_order_frame, text="Nuevo Pedido")
        order_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        order_panel.grid_columnconfigure(1, weight=1, minsize=200)
        
        ttk.Label(order_panel, text="Producto:", width=15).grid(row=0, column=0, pady=5, padx=15)
        product_combo = ttk.Combobox(order_panel, 
                                  textvariable=self.drink_var,
                                  values=list(self.precio_productos.keys()),
                                  state="readonly")
        product_combo.grid(row=0, column=1, pady=5, padx=15)

        ttk.Label(order_panel, text="Cantidad:", width=15).grid(row=1, column=0, pady=5, padx=15)
        ttk.Spinbox(order_panel, from_=1, to=10,
                   textvariable=self.cantidad_var,
                   state="readonly",
                   wrap=True).grid(row=1, column=1, pady=5, padx=15)
        
        ttk.Button(order_panel, text="Agregar al Carrito",
                 command=self.agregar_al_carrito).grid(
            row=3, column=0, columnspan=2, pady=10, padx=15, sticky="ew")
        
        # Carrito
        cart_frame = ttk.LabelFrame(self.new_order_frame, text="Carrito")
        cart_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        cart_frame.grid_rowconfigure(0, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)
        
        text_frame = ttk.Frame(cart_frame)
        text_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.cart_text = tk.Text(text_frame, height=10, width=40)
        self.cart_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.cart_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.cart_text.configure(yscrollcommand=scrollbar.set)
        
        self.total_label = ttk.Label(cart_frame, text="Total: Q0.00")
        self.total_label.grid(row=1, column=0, sticky="w", padx=15, pady=10)
        
        # Botones
        button_frame = ttk.Frame(cart_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Vaciar Carrito",
                  command=self.vaciar_carrito).pack(side="left", padx=10)
        
        ttk.Button(button_frame, text="Crear Pedido",
                  command=self.confirmar_orden).pack(side="left", padx=10)
        
        ttk.Button(button_frame, text="Imprimir Factura",
                  command=self.imprimir_factura).pack(side="left", padx=10)

    def agregar_al_carrito(self):
        producto_seleccionado = self.drink_var.get()
        cantidad = self.cantidad_var.get()
        
        if not producto_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
            
        stock_disponible = self.stock_productos.get(producto_seleccionado, 0)
        
        if stock_disponible <= 0:
            messagebox.showwarning("Sin Stock", f"No hay stock disponible de {producto_seleccionado}")
            return
            
        if cantidad > stock_disponible:
            messagebox.showwarning("Stock Insuficiente", 
                                f"Solo hay {stock_disponible} unidades disponibles de {producto_seleccionado}")
            return
            
        producto = ProductoTextil(producto_seleccionado, cantidad, stock_disponible)
        self.productos_en_carrito.append(producto)
        self.actualizar_carrito()
        
        # Limpiar selección
        self.drink_var.set('')
        self.cantidad_var.set(1)

    def actualizar_carrito(self):
        self.cart_text.delete(1.0, tk.END)
        total = 0
        
        for i, producto in enumerate(self.productos_en_carrito, 1):
            subtotal = producto.calcular_subtotal(self.precio_productos)
            total += subtotal
            
            self.cart_text.insert(tk.END, 
                f"{i}. {producto}\n   Subtotal: Q{subtotal:.2f}\n\n")
        
        self.total_label.config(text=f"Total: Q{total:.2f}")

    def vaciar_carrito(self):
        if self.productos_en_carrito and messagebox.askyesno(
            "Confirmar", "¿Está seguro de vaciar el carrito?"):
            self.productos_en_carrito = []
            self.actualizar_carrito()

    def confirmar_orden(self):
        if not self.productos_en_carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
            
        # Verificar stock antes de confirmar
        for producto in self.productos_en_carrito:
            stock_disponible = self.stock_productos.get(producto.tipo, 0)
            if producto.cantidad > stock_disponible:
                messagebox.showwarning("Stock Insuficiente", 
                                    f"No hay suficiente stock de {producto.tipo} (Stock: {stock_disponible})")
                return
        
        total = sum(producto.calcular_subtotal(self.precio_productos) 
                   for producto in self.productos_en_carrito)
        
        # Obtener datos del cliente
        self.cliente_actual = Cliente(
            self.cliente_nombre_var.get(),
            self.cliente_nit_var.get(),
            self.cliente_pago_var.get()
        )
        
        confirm_msg = "¿Confirmar pedido?\n\n"
        confirm_msg += f"Cliente: {self.cliente_actual.nombre}\n"
        confirm_msg += f"NIT: {self.cliente_actual.nit}\n"
        confirm_msg += f"Método de Pago: {self.cliente_actual.metodo_pago}\n\n"
        
        for i, producto in enumerate(self.productos_en_carrito, 1):
            subtotal = producto.calcular_subtotal(self.precio_productos)
            confirm_msg += f"{i}. {producto}\n   Subtotal: Q{subtotal:.2f}\n\n"
        confirm_msg += f"\nTotal: Q{total:.2f}"
        
        if messagebox.askyesno("Confirmar Pedido", confirm_msg):
            # Generar ticket
            ticket = self.generar_ticket(self.contador_orden, 
                                       self.productos_en_carrito.copy(), 
                                       total,
                                       self.cliente_actual)
            
            # Crear la orden
            self.crear_orden()
            
            # Limpiar carrito y datos del cliente
            self.productos_en_carrito = []
            self.actualizar_carrito()
            self.cliente_nombre_var.set("")
            self.cliente_nit_var.set("")
            self.cliente_pago_var.set("Efectivo")
            
            # Mostrar mensaje de éxito
            success_msg = f"¡Pedido creado exitosamente!\n\nTicket #{ticket.ticket_id}"
            messagebox.showinfo("Éxito", success_msg)
            
            # Preguntar si desea ver/imprimir el ticket
            if messagebox.askyesno("Ticket", "¿Desea ver el detalle del ticket?"):
                self.mostrar_detalle_ticket(ticket)
            
            # Actualizar lista de tickets
            self.actualizar_lista_tickets()
            
            # Cambiar a la pestaña de pedidos activos
            self.notebook.select(1)

    def imprimir_factura(self):
        if not self.productos_en_carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
            
        # Obtener datos del cliente
        self.cliente_actual = Cliente(
            self.cliente_nombre_var.get(),
            self.cliente_nit_var.get(),
            self.cliente_pago_var.get()
        )
        
        total = sum(producto.calcular_subtotal(self.precio_productos) 
                   for producto in self.productos_en_carrito)
        
        # Crear un ticket temporal para la previsualización
        ticket = Ticket("PREVIEW", self.productos_en_carrito.copy(), total, self.cliente_actual)
        self.mostrar_detalle_ticket(ticket, imprimir=True)

    def mostrar_detalle_ticket(self, ticket, imprimir=False):
        detalle = tk.Toplevel(self.window)
        detalle.title(f"Ticket #{ticket.ticket_id}")
        detalle.geometry("500x700")
        
        main_frame = ttk.Frame(detalle, style="Ticket.TFrame")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Encabezado
        ttk.Label(main_frame, text=ticket.establecimiento,
                style="TicketTitle.TLabel").pack(pady=5)
        
        # Información de ubicación
        ttk.Label(main_frame, text=ticket.ciudad,
                style="Ticket.TLabel").pack(pady=1)
        ttk.Label(main_frame, text=ticket.direccion,
                style="Ticket.TLabel").pack(pady=1)
        ttk.Label(main_frame, text=f"Tel: {ticket.telefono}",
                style="Ticket.TLabel").pack(pady=1)
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Información del cliente
        ttk.Label(main_frame, text="Datos del Cliente:",
                style="TicketHeader.TLabel").pack()
        ttk.Label(main_frame, text=f"Nombre: {ticket.cliente.nombre}",
                style="Ticket.TLabel").pack()
        ttk.Label(main_frame, text=f"NIT: {ticket.cliente.nit}",
                style="Ticket.TLabel").pack()
        ttk.Label(main_frame, text=f"Pago: {ticket.cliente.metodo_pago}",
                style="Ticket.TLabel").pack()
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Información del ticket
        ttk.Label(main_frame, text=f"Ticket: #{ticket.ticket_id}",
                style="TicketHeader.TLabel").pack()
        ttk.Label(main_frame, 
                text=f"Fecha: {ticket.timestamp.strftime('%d/%m/%Y %H:%M')}",
                style="Ticket.TLabel").pack()
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Detalles de productos
        for producto in ticket.productos:
            producto_frame = ttk.Frame(main_frame, style="Ticket.TFrame")
            producto_frame.pack(fill='x', pady=2)
            ttk.Label(producto_frame, text=str(producto),
                    style="Ticket.TLabel").pack(side='left')
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Total
        ttk.Label(main_frame, text=f"Total: Q{ticket.total:.2f}",
                style="TicketTotal.TLabel").pack(pady=5)
        
        # Redes sociales
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(main_frame, text="Síguenos en:",
                style="Ticket.TLabel").pack(pady=(5,0))
        for red, usuario in ticket.redes_sociales.items():
            ttk.Label(main_frame, text=f"{red}: {usuario}",
                    style="Ticket.TLabel").pack()
        
        # Mensaje final
        ttk.Label(main_frame, text="\n¡Gracias por su preferencia!",
                style="TicketHeader.TLabel").pack(pady=(10,5))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        if imprimir:
            ttk.Button(button_frame, text="Confirmar Impresión",
                      command=lambda: self.imprimir_ticket(ticket)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cerrar",
                  command=detalle.destroy).pack(side='left', padx=5)

    def imprimir_ticket(self, ticket):
        try:
            # Crear un archivo temporal con el ticket
            filename = os.path.join(self.data_dir, f"ticket_{ticket.ticket_id}.txt")
            with open(filename, 'w') as f:
                f.write(f"{ticket.establecimiento}\n")
                f.write(f"{ticket.ciudad}\n")
                f.write(f"{ticket.direccion}\n")
                f.write(f"Tel: {ticket.telefono}\n\n")
                f.write("Datos del Cliente:\n")
                f.write(f"Nombre: {ticket.cliente.nombre}\n")
                f.write(f"NIT: {ticket.cliente.nit}\n")
                f.write(f"Pago: {ticket.cliente.metodo_pago}\n\n")
                f.write(f"Ticket: #{ticket.ticket_id}\n")
                f.write(f"Fecha: {ticket.timestamp.strftime('%d/%m/%Y %H:%M')}\n\n")
                f.write("Productos:\n")
                for producto in ticket.productos:
                    f.write(f"{producto}\n")
                f.write(f"\nTotal: Q{ticket.total:.2f}\n\n")
                f.write("¡Gracias por su preferencia!\n")
            
            # Simular impresión (en Windows)
            os.startfile(filename, "print")
            messagebox.showinfo("Éxito", "Ticket enviado a impresión")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir el ticket: {str(e)}")

    def setup_ordenes_activas_tab(self):
        self.ordenes_activas_frame.grid_columnconfigure(0, weight=1)
        self.ordenes_activas_frame.grid_columnconfigure(1, weight=0)
        self.ordenes_activas_frame.grid_columnconfigure(2, weight=1)
        self.ordenes_activas_frame.grid_rowconfigure(1, weight=1)
        
        # Panel izquierdo: Pedidos en Preparación
        preparing_panel = ttk.Frame(self.ordenes_activas_frame)
        preparing_panel.grid(row=0, rowspan=2, column=0, sticky="nsew", padx=5, pady=5)
        preparing_panel.grid_rowconfigure(1, weight=1)
        preparing_panel.grid_columnconfigure(0, weight=1)
        
        ttk.Label(preparing_panel, text="Pedidos en Preparación", 
                style="Header.TLabel").grid(row=0, column=0, pady=5, sticky="w")
        
        # Scrollbar y Canvas para pedidos en preparación
        preparing_scroll = ttk.Scrollbar(preparing_panel)
        preparing_scroll.grid(row=1, column=1, sticky="ns")
        
        self.preparing_canvas = tk.Canvas(preparing_panel, 
                                        yscrollcommand=preparing_scroll.set,
                                        highlightthickness=0)
        self.preparing_canvas.grid(row=1, column=0, sticky="nsew")
        
        self.preparing_frame = ttk.Frame(self.preparing_canvas)
        self.preparing_frame.grid_columnconfigure(0, weight=1)
        
        self.preparing_canvas.create_window((0, 0), 
                                        window=self.preparing_frame,
                                        anchor="nw",
                                        tags="preparing_frame")
        
        preparing_scroll.config(command=self.preparing_canvas.yview)
        
        # Separador vertical
        ttk.Separator(self.ordenes_activas_frame, orient='vertical').grid(
            row=0, rowspan=2, column=1, sticky="ns", padx=10)
        
        # Panel derecho: Pedidos Listos
        completed_panel = ttk.Frame(self.ordenes_activas_frame)
        completed_panel.grid(row=0, rowspan=2, column=2, sticky="nsew", padx=5, pady=5)
        completed_panel.grid_rowconfigure(1, weight=1)
        completed_panel.grid_columnconfigure(0, weight=1)
        
        ttk.Label(completed_panel, text="Pedidos Listos", 
                style="Header.TLabel").grid(row=0, column=0, pady=5, sticky="w")
        
        completed_scroll = ttk.Scrollbar(completed_panel)
        completed_scroll.grid(row=1, column=1, sticky="ns")
        
        self.completed_canvas = tk.Canvas(completed_panel, 
                                        yscrollcommand=completed_scroll.set,
                                        highlightthickness=0)
        self.completed_canvas.grid(row=1, column=0, sticky="nsew")
        
        self.completed_frame = ttk.Frame(self.completed_canvas)
        self.completed_frame.grid_columnconfigure(0, weight=1)
        
        self.completed_canvas.create_window((0, 0), 
                                        window=self.completed_frame,
                                        anchor="nw", 
                                        tags="completed_frame")
        
        completed_scroll.config(command=self.completed_canvas.yview)
        
        # Configurar eventos para mantener la responsividad
        self.preparing_frame.bind('<Configure>', self.conf_on_frame)
        self.completed_frame.bind('<Configure>', self.conf_on_frame)

    def crear_orden(self):
        if not self.productos_en_carrito:
            return
                    
        order_number = self.contador_orden
        self.contador_orden += 1
        
        # Crear frame del pedido
        order_frame = ttk.LabelFrame(self.preparing_frame, text=f"Pedido #{order_number}")
        order_frame.grid(row=len(self.ordenes_activas), column=0, sticky="ew", padx=5, pady=5)
        order_frame.grid_columnconfigure(0, weight=1)
        
        content_frame = ttk.Frame(order_frame)
        content_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Mostrar productos
        for i, producto in enumerate(self.productos_en_carrito):
            ttk.Label(content_frame, text=str(producto)).grid(
                row=i, column=0, pady=2, sticky="ew")
        
        # Botón para marcar como listo
        ttk.Button(content_frame, text="Marcar como Listo",
                command=lambda num=order_number: self.marcar_como_listo(num)).grid(
                    row=len(self.productos_en_carrito), column=0, pady=5)
        
        # Guardar información del pedido
        self.ordenes_activas[order_number] = {
            'frame': order_frame,
            'productos': self.productos_en_carrito.copy()
        }
    
    def marcar_como_listo(self, order_number):
        if order_number in self.ordenes_activas:
                order = self.ordenes_activas[order_number]
                original_frame = order['frame']
                
                # Crear nuevo frame en la sección de completados
                completed_frame = ttk.LabelFrame(self.completed_frame, text=f"Pedido #{order_number}")
                completed_frame.grid(sticky="ew", padx=5, pady=5)
                completed_frame.grid_columnconfigure(0, weight=1)
                
                # Frame para el contenido
                content_frame = ttk.Frame(completed_frame)
                content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
                content_frame.grid_columnconfigure(0, weight=1)
                
                # Mostrar los productos
                for idx, producto in enumerate(order['productos']):
                    producto_frame = ttk.Frame(content_frame)
                    producto_frame.grid(row=idx, column=0, sticky="ew")
                    producto_frame.grid_columnconfigure(0, weight=1)
                    
                    ttk.Label(producto_frame, text=str(producto)).grid(
                        row=0, column=0, sticky="w", pady=2)
                
                # Mensaje de completado
                ttk.Label(content_frame, text="¡Pedido Completado!", 
                        style="Header.TLabel").grid(
                            row=len(order['productos']), column=0, sticky="ew", pady=5)
                
                # Botón eliminar
                ttk.Button(content_frame, text="Eliminar",
                        command=lambda num=order_number: self.remover_orden(num)).grid(
                            row=len(order['productos'])+1, column=0, pady=5)
                
                # Actualizar la referencia del frame en ordenes_activas
                order['frame'] = completed_frame
                
                # IMPORTANTE: Destruir el frame original DESPUÉS de crear el nuevo
                original_frame.destroy()
                
                # Actualizar los canvas para reflejar los cambios
                self.window.after(100, self.update_canvases)

    def on_tab_change(self, event):
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        
        if tab_index == 1:
            self.window.after(100, self.update_canvases)

    def conf_on_frame(self, event):
        canvas = event.widget.master
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig("preparing_frame", width=canvas.winfo_width())
        canvas.itemconfig("completed_frame", width=canvas.winfo_width())

    def update_canvases(self):
        try:
            if self.preparing_canvas and self.preparing_frame:
                self.preparing_canvas.configure(scrollregion=self.preparing_canvas.bbox("all"))
                self.preparing_canvas.itemconfig("preparing_frame", 
                                            width=self.preparing_canvas.winfo_width())
                
            if self.completed_canvas and self.completed_frame:
                self.completed_canvas.configure(scrollregion=self.completed_canvas.bbox("all"))
                self.completed_canvas.itemconfig("completed_frame", 
                                            width=self.completed_canvas.winfo_width())
                
            # Forzar actualización visual
            self.window.update_idletasks()
        except tk.TclError:
            pass  # Ignorar errores si los widgets fueron destruidos

    def conf_precio_menu(self):
        # Creacion del frame contenedor para menú de precios e información
        self.right_panel = ttk.Frame(self.window)
        self.right_panel.grid(row=1, column=1, sticky="n", padx=10, pady=5)
        
        # Price menu panel
        price_frame = ttk.LabelFrame(self.right_panel, text="Menú de Precios")
        price_frame.grid(row=0, column=0, sticky="n", pady=(0,5))
        
        # Encabezados
        ttk.Label(price_frame, text="", style="Bold.TLabelframe.Label").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(5,2))
        
        # Headers for columns
        ttk.Label(price_frame, text="Producto", style="Bold.TLabelframe.Label").grid(
            row=1, column=0, sticky="w", padx=5)
        ttk.Label(price_frame, text="Precio", style="Bold.TLabelframe.Label").grid(
            row=1, column=1, sticky="e", padx=5)
        
        row = 2
        for producto, precio in self.precio_productos.items():
            ttk.Label(price_frame, text=producto).grid(
                row=row, column=0, sticky="w", padx=5)
            ttk.Label(price_frame, text=f"Q{precio:.2f}").grid(
                row=row, column=1, sticky="e", padx=5)
            row += 1

    def setup_info_panel(self):
        """Configura el panel de información con fecha, hora y ubicación"""
        info_frame = ttk.LabelFrame(self.right_panel, text="Información")
        info_frame.grid(row=1, column=0, sticky="n", pady=(0,5))
        
        self.time_label = ttk.Label(info_frame, text="")
        self.time_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        self.actualizar_tiempo()
        
        current_date = datetime.now().strftime("%d/%m/%Y")
        ttk.Label(info_frame, text=f"Fecha: {current_date}",
                style="Bold.TLabelframe.Label").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Ubicación:",
                style="Bold.TLabelframe.Label").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(10,2))
        
        ttk.Label(info_frame, text="Ciudad, País").grid(
            row=3, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Dirección:",
                style="Bold.TLabelframe.Label").grid(
            row=4, column=0, columnspan=2, sticky="w", padx=5, pady=(10,2))
        
        direccion_text = "Dirección de la empresa"
        ttk.Label(info_frame, text=direccion_text).grid(
            row=5, column=0, columnspan=2, sticky="w", padx=5, pady=2)

    def actualizar_tiempo(self):
        """Actualiza la hora en tiempo real"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=f"Hora: {current_time}")
        # Actualizar cada segundo
        self.window.after(1000, self.actualizar_tiempo)

    def remover_orden(self, order_number):
        if order_number in self.ordenes_activas:
            if self.ordenes_activas[order_number]['frame'].winfo_exists():
                self.ordenes_activas[order_number]['frame'].destroy()
            del self.ordenes_activas[order_number]
            self.update_canvases()

    def buscar_ticket(self):
        ticket_id = tk.simpledialog.askstring("Buscar Ticket", 
                                            "Ingrese el ID del ticket:")
        if ticket_id:
            ticket = next((t for t in self.tickets if t.ticket_id == ticket_id.upper()), 
                         None)
            if ticket:
                self.mostrar_detalle_ticket(ticket)
            else:
                messagebox.showwarning("No encontrado", 
                                     "No se encontró el ticket especificado")

    def exportar_tickets(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump([t.to_dict() for t in self.tickets], f, indent=4)
                messagebox.showinfo("Éxito", "Tickets exportados correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar tickets: {str(e)}")

    def salir(self):
        # Guardar tickets antes de salir
        self.guardar_datos()
        self.window.quit()

    def mostrar_creditos(self):
        credits_text = "Sistema de Pedidos para Textiles Rosy\n\nDesarrollado por: [Tu nombre o empresa]\n\nVersión 1.0"
        messagebox.showinfo("Créditos", credits_text)

    def mostrar_ayuda(self):
        texto_ayuda = """
    Bienvenido al Sistema de Pedidos de Textiles Rosy

    1. Realizar un Nuevo Pedido:
       - Selecciona productos y agrégalos al carrito.
       - Haz clic en "Crear Pedido" para generar un ticket.

    2. Gestionar Pedidos Activos:
       - Marca los pedidos como listos o elimínalos si ya no son necesarios.

    3. Ver el Historial de Tickets:
       - Busca y revisa los tickets anteriores.

    4. Gestionar Inventario:
       - Actualiza el stock de productos desde el menú Inventario.

    5. Datos del Cliente:
       - Ingresa nombre, NIT y método de pago antes de crear pedidos.

    6. Imprimir Facturas:
       - Genera facturas con los datos del cliente.

    7. Exportar Datos:
       - Exporta tickets e inventario a diferentes formatos.

    8. Consejos Adicionales:
       - Mantén actualizados los precios y stock de productos.

    9. Soporte y Contacto:
       - Contáctanos si necesitas ayuda.
    """
        messagebox.showinfo("Ayuda - Cómo Funciona", texto_ayuda)

    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.salir)
        self.window.mainloop()

def iniciar_modulo_pedidos(root=None):
    app = SistemaPedidosTextiles(root)
    return app

if __name__ == "__main__":
    app = SistemaPedidosTextiles()
    app.run()