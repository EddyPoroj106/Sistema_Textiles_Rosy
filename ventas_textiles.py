import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import uuid
from tkcalendar import DateEntry

class VentasTextiles:
    def __init__(self, root=None, inventario=None):
        self.root = root
        self.window = tk.Toplevel(root) if root else tk.Tk()
        self.window.title("Sistema de Ventas - Textiles Rosy")
        self.window.geometry("1200x800")
        
        # Control para evitar múltiples instancias
        self.window.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        
        # Conexión con inventario
        self.inventario = inventario
        
        # Configuración de archivos
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.ventas_file = os.path.join(self.data_dir, "ventas.json")
        self.ventas = self.cargar_ventas()
        
        # Variables para el panel de productos
        self.panel_productos_abierto = False
        
        # Configurar interfaz
        self.conf_estilo()
        self.conf_gui()
    
    def cerrar_ventana(self):
        """Maneja el cierre de la ventana"""
        self.guardar_ventas()
        self.window.destroy()
        if not self.root:  # Si es la ventana principal
            try:
                self.root.quit()
            except:
                pass
    
    def conf_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        PRIMARY_COLOR = "#4a90e2"
        SECONDARY_COLOR = "#2c3e50"
        BG_COLOR = "#f5f6fa"
        
        style.configure(".", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TButton", background=PRIMARY_COLOR, foreground="white")
        style.configure("Treeview", fieldbackground=BG_COLOR, background=BG_COLOR)
        style.configure("Treeview.Heading", background=PRIMARY_COLOR, foreground="white")
    
    def cargar_ventas(self):
        if os.path.exists(self.ventas_file):
            try:
                with open(self.ventas_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def guardar_ventas(self):
        with open(self.ventas_file, 'w') as f:
            json.dump(self.ventas, f, indent=4)
    
    def conf_gui(self):
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Pestaña de Nueva Venta
        self.nueva_venta_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.nueva_venta_frame, text="Nueva Venta")
        self.conf_nueva_venta_tab()
        
        # Pestaña de Historial
        self.historial_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.historial_frame, text="Historial de Ventas")
        self.conf_historial_tab()
    
    def conf_nueva_venta_tab(self):
        # Frame principal con paneles divididos
        main_frame = ttk.Frame(self.nueva_venta_frame)
        main_frame.pack(expand=True, fill='both')
        
        # Panel izquierdo (formulario de venta)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        # Panel derecho (lista de productos)
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)
        
        # Contenido panel izquierdo
        self.conf_panel_venta(left_frame)
        
        # Contenido panel derecho
        self.conf_panel_productos(right_frame)
    
    def conf_panel_venta(self, parent_frame):
        # Panel de cliente
        cliente_frame = ttk.LabelFrame(parent_frame, text="Datos del Cliente")
        cliente_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(cliente_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=2, sticky='e')
        self.cliente_nombre = ttk.Entry(cliente_frame)
        self.cliente_nombre.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(cliente_frame, text="NIT:").grid(row=1, column=0, padx=5, pady=2, sticky='e')
        self.cliente_nit = ttk.Entry(cliente_frame)
        self.cliente_nit.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(cliente_frame, text="Método de Pago:").grid(row=2, column=0, padx=5, pady=2, sticky='e')
        self.metodo_pago = ttk.Combobox(cliente_frame, values=["Efectivo", "Tarjeta", "Transferencia"])
        self.metodo_pago.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        self.metodo_pago.set("Efectivo")
        
        # Panel de productos
        producto_frame = ttk.LabelFrame(parent_frame, text="Agregar Productos")
        producto_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(producto_frame, text="Menú Productos", 
                  command=self.abrir_menu_productos).grid(row=0, column=0, padx=5, pady=2)
        
        ttk.Label(producto_frame, text="Producto:").grid(row=0, column=1, padx=5, pady=2)
        self.producto_var = tk.StringVar()
        productos = list(self.inventario.productos.keys()) if self.inventario else []
        self.producto_cb = ttk.Combobox(producto_frame, textvariable=self.producto_var, 
                                      values=productos, state='readonly')
        self.producto_cb.grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(producto_frame, text="Cantidad:").grid(row=0, column=3, padx=5, pady=2)
        self.cantidad_var = tk.IntVar(value=1)
        ttk.Spinbox(producto_frame, from_=1, to=100, textvariable=self.cantidad_var).grid(row=0, column=4, padx=5, pady=2)
        
        ttk.Button(producto_frame, text="Agregar", command=self.agregar_producto).grid(row=0, column=5, padx=5, pady=2)
        ttk.Button(producto_frame, text="Refrescar", command=self.refrescar_datos).grid(row=0, column=6, padx=5, pady=2)
        
        # Carrito de compras
        carrito_frame = ttk.LabelFrame(parent_frame, text="Carrito de Compras")
        carrito_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        columns = ('producto', 'cantidad', 'precio', 'subtotal')
        self.carrito_tree = ttk.Treeview(carrito_frame, columns=columns, show='headings')
        
        self.carrito_tree.heading('producto', text='Producto')
        self.carrito_tree.heading('cantidad', text='Cantidad')
        self.carrito_tree.heading('precio', text='Precio Unitario')
        self.carrito_tree.heading('subtotal', text='Subtotal')
        
        scrollbar = ttk.Scrollbar(carrito_frame, orient='vertical', command=self.carrito_tree.yview)
        self.carrito_tree.configure(yscrollcommand=scrollbar.set)
        
        self.carrito_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Total y botones
        total_frame = ttk.Frame(parent_frame)
        total_frame.pack(fill='x', padx=10, pady=5)
        
        self.total_var = tk.StringVar(value="Total: Q0.00")
        ttk.Label(total_frame, textvariable=self.total_var, font=('Arial', 12, 'bold')).pack(side='left')
        
        btn_frame = ttk.Frame(total_frame)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="Vaciar Carrito", command=self.vaciar_carrito).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Finalizar Venta", command=self.finalizar_venta).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Imprimir Factura", command=self.imprimir_factura).pack(side='left', padx=5)
        
        # Inicializar carrito
        self.carrito = []
    
    def conf_panel_productos(self, parent_frame):
        """Configura el panel derecho con la lista de productos y precios"""
        self.productos_frame = ttk.LabelFrame(parent_frame, text="Productos Disponibles", padding=10)
        self.productos_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(self.productos_frame)
        scrollbar = ttk.Scrollbar(self.productos_frame, orient='vertical', command=canvas.yview)
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
        
        # Mostrar productos
        self.actualizar_panel_productos(scrollable_frame)
    
    def actualizar_panel_productos(self, frame):
        """Actualiza el panel de productos con los datos actuales"""
        # Limpiar frame
        for widget in frame.winfo_children():
            widget.destroy()
        
        if not self.inventario:
            ttk.Label(frame, text="No hay conexión con el inventario").pack()
            return
            
        # Mostrar productos con formato
        for producto, precio in self.inventario.productos.items():
            stock = self.inventario.stock.get(producto, 0)
            producto_frame = ttk.Frame(frame)
            producto_frame.pack(fill='x', pady=2)
            
            ttk.Label(producto_frame, text=producto, width=25, anchor='w').pack(side='left')
            ttk.Label(producto_frame, text=f"Q{precio:.2f}", width=10, anchor='e').pack(side='left')
            ttk.Label(producto_frame, text=f"Stock: {stock}", width=10, anchor='e').pack(side='left')
    
    def refrescar_datos(self):
        """Refresca los datos del inventario y actualiza las interfaces"""
        if self.inventario:
            self.inventario.cargar_datos()
            self.producto_cb['values'] = list(self.inventario.productos.keys())
            self.actualizar_panel_productos(self.productos_frame.winfo_children()[0].winfo_children()[0])
            messagebox.showinfo("Actualizado", "Datos de productos refrescados")
    
    def abrir_menu_productos(self):
        if not self.inventario:
            messagebox.showwarning("Error", "No hay conexión con el inventario")
            return
            
        def seleccionar_producto(producto):
            self.producto_var.set(producto)
            if producto in self.inventario.productos:
                self.cantidad_var.set(1)
        
        # Evitar abrir múltiples ventanas
        if not hasattr(self, 'menu_productos') or not self.menu_productos.window.winfo_exists():
            self.menu_productos = MenuProductos(self.window, self.inventario, seleccionar_producto)
        else:
            self.menu_productos.window.lift()
    
    def agregar_producto(self):
        producto = self.producto_var.get()
        cantidad = self.cantidad_var.get()
        
        if not producto:
            messagebox.showwarning("Error", "Seleccione un producto")
            return
            
        if cantidad <= 0:
            messagebox.showwarning("Error", "Cantidad inválida")
            return
            
        # Verificar stock
        if self.inventario and self.inventario.stock.get(producto, 0) < cantidad:
            messagebox.showwarning("Stock Insuficiente", 
                                 f"No hay suficiente stock de {producto}")
            return
            
        precio = self.inventario.productos[producto] if self.inventario else 0
        subtotal = precio * cantidad
        
        self.carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': subtotal
        })
        
        self.actualizar_carrito()
        self.producto_var.set('')
        self.cantidad_var.set(1)
    
    def actualizar_carrito(self):
        for item in self.carrito_tree.get_children():
            self.carrito_tree.delete(item)
            
        total = 0
        for item in self.carrito:
            self.carrito_tree.insert('', 'end', values=(
                item['producto'],
                item['cantidad'],
                f"Q{item['precio']:.2f}",
                f"Q{item['subtotal']:.2f}"
            ))
            total += item['subtotal']
        
        self.total_var.set(f"Total: Q{total:.2f}")
    
    def vaciar_carrito(self):
        if self.carrito and messagebox.askyesno("Confirmar", "¿Vaciar el carrito?"):
            self.carrito = []
            self.actualizar_carrito()
    
    def finalizar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Error", "El carrito está vacío")
            return
            
        nombre = self.cliente_nombre.get().strip()
        nit = self.cliente_nit.get().strip()
        metodo_pago = self.metodo_pago.get()
        
        if not nombre:
            messagebox.showwarning("Error", "Ingrese el nombre del cliente")
            return
            
        # Crear venta
        venta = {
            'id': str(uuid.uuid4())[:8],
            'fecha': datetime.now().isoformat(),
            'cliente': {
                'nombre': nombre,
                'nit': nit,
                'metodo_pago': metodo_pago
            },
            'productos': self.carrito,
            'total': sum(item['subtotal'] for item in self.carrito)
        }
        
        # Actualizar inventario
        if self.inventario:
            for item in self.carrito:
                producto = item['producto']
                cantidad = item['cantidad']
                if producto in self.inventario.stock:
                    self.inventario.stock[producto] -= cantidad
                    if self.inventario.stock[producto] < 0:
                        self.inventario.stock[producto] = 0
            self.inventario.guardar_datos()
        
        # Guardar venta
        self.ventas.append(venta)
        self.guardar_ventas()
        
        # Mostrar resumen
        resumen = f"Venta registrada exitosamente\n\nID: {venta['id']}\n"
        resumen += f"Cliente: {nombre}\n"
        resumen += f"Total: Q{venta['total']:.2f}\n\n"
        resumen += "¿Desea imprimir la factura?"
        
        if messagebox.askyesno("Venta Exitosa", resumen):
            self.imprimir_factura(venta)
        
        # Reiniciar interfaz
        self.carrito = []
        self.actualizar_carrito()
        self.cliente_nombre.delete(0, 'end')
        self.cliente_nit.delete(0, 'end')
        self.metodo_pago.set("Efectivo")
        
        # Actualizar panel de productos
        self.refrescar_datos()
    
    def imprimir_factura(self, venta=None):
        if not venta:
            if not self.carrito:
                messagebox.showwarning("Error", "No hay productos en el carrito")
                return
                
            venta = {
                'id': 'PREVIEW',
                'fecha': datetime.now().isoformat(),
                'cliente': {
                    'nombre': self.cliente_nombre.get().strip() or "CONSUMIDOR FINAL",
                    'nit': self.cliente_nit.get().strip() or "CF",
                    'metodo_pago': self.metodo_pago.get()
                },
                'productos': self.carrito,
                'total': sum(item['subtotal'] for item in self.carrito)
            }
        
        # Crear ventana de factura
        factura = tk.Toplevel(self.window)
        factura.title(f"Factura #{venta['id']}")
        factura.geometry("400x600")
        
        # Contenido de la factura
        content = tk.Text(factura, wrap='word')
        content.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Encabezado
        content.insert('end', "Textiles Rosy\n", 'center')
        content.insert('end', "Dirección: Dirección de la empresa\n", 'center')
        content.insert('end', "Teléfono: Teléfono de contacto\n\n", 'center')
        
        # Datos de la factura
        content.insert('end', f"FACTURA: #{venta['id']}\n")
        content.insert('end', f"Fecha: {datetime.fromisoformat(venta['fecha']).strftime('%d/%m/%Y %H:%M')}\n\n")
        
        # Datos del cliente
        content.insert('end', "DATOS DEL CLIENTE:\n", 'bold')
        content.insert('end', f"Nombre: {venta['cliente']['nombre']}\n")
        content.insert('end', f"NIT: {venta['cliente']['nit']}\n")
        content.insert('end', f"Método de pago: {venta['cliente']['metodo_pago']}\n\n")
        
        # Productos
        content.insert('end', "PRODUCTOS:\n", 'bold')
        for item in venta['productos']:
            content.insert('end', 
                         f"{item['cantidad']} x {item['producto']} - Q{item['precio']:.2f} = Q{item['subtotal']:.2f}\n")
        
        # Total
        content.insert('end', "\nTOTAL: ", 'bold')
        content.insert('end', f"Q{venta['total']:.2f}\n\n", 'bold')
        
        # Mensaje final
        content.insert('end', "\n¡Gracias por su compra!\n", 'center')
        content.insert('end', "Vuelva pronto\n", 'center')
        
        # Configurar tags para formato
        content.tag_configure('center', justify='center')
        content.tag_configure('bold', font=('Arial', 10, 'bold'))
        
        # Configurar como solo lectura
        content.config(state='disabled')
        
        # Botón de impresión
        btn_frame = ttk.Frame(factura)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Imprimir", 
                  command=lambda: self.imprimir_texto(content.get("1.0", "end"))).pack(side='left')
        ttk.Button(btn_frame, text="Cerrar", command=factura.destroy).pack(side='right')
    
    def imprimir_texto(self, texto):
        try:
            filename = os.path.join(self.data_dir, "factura_temp.txt")
            with open(filename, 'w') as f:
                f.write(texto)
            
            # Simular impresión (Windows)
            os.startfile(filename, "print")
            messagebox.showinfo("Éxito", "Factura enviada a impresión")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir: {str(e)}")
    
    def conf_historial_tab(self):
        # Frame principal
        main_frame = ttk.Frame(self.historial_frame)
        main_frame.pack(expand=True, fill='both')
        
        # Filtros
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Fecha:").pack(side='left', padx=5)
        self.fecha_filtro = DateEntry(filter_frame, date_pattern='dd/mm/yyyy')
        self.fecha_filtro.pack(side='left', padx=5)
        
        ttk.Label(filter_frame, text="Buscar:").pack(side='left', padx=5)
        self.busqueda_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.busqueda_var).pack(side='left', padx=5)
        
        ttk.Button(filter_frame, text="Filtrar", command=self.filtrar_ventas).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Limpiar", command=self.limpiar_filtros).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Refrescar", command=self.refrescar_historial).pack(side='left', padx=5)
        
        # Tabla de ventas
        columns = ('id', 'fecha', 'cliente', 'total')
        self.ventas_tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        self.ventas_tree.heading('id', text='ID Venta')
        self.ventas_tree.heading('fecha', text='Fecha')
        self.ventas_tree.heading('cliente', text='Cliente')
        self.ventas_tree.heading('total', text='Total')
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.ventas_tree.yview)
        self.ventas_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ventas_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Ver Detalle", command=self.ver_detalle_venta).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Exportar", command=self.exportar_ventas).pack(side='left', padx=5)
        
        # Cargar datos iniciales
        self.actualizar_historial()
    
    def refrescar_historial(self):
        """Refresca el historial de ventas desde el archivo"""
        self.ventas = self.cargar_ventas()
        self.actualizar_historial()
        messagebox.showinfo("Actualizado", "Historial de ventas refrescado")
    
    def filtrar_ventas(self):
        fecha = self.fecha_filtro.get_date()
        busqueda = self.busqueda_var.get().lower()
        
        ventas_filtradas = []
        for venta in self.ventas:
            venta_date = datetime.fromisoformat(venta['fecha']).date()
            if venta_date == fecha:
                if not busqueda or (
                    busqueda in venta['id'].lower() or
                    busqueda in venta['cliente']['nombre'].lower() or
                    busqueda in str(venta['total']).lower()
                ):
                    ventas_filtradas.append(venta)
        
        self.actualizar_historial(ventas_filtradas)
    
    def limpiar_filtros(self):
        self.fecha_filtro.set_date(datetime.now())
        self.busqueda_var.set('')
        self.actualizar_historial()
    
    def actualizar_historial(self, ventas=None):
        for item in self.ventas_tree.get_children():
            self.ventas_tree.delete(item)
            
        ventas_a_mostrar = ventas if ventas is not None else self.ventas
        
        for venta in reversed(ventas_a_mostrar):
            fecha = datetime.fromisoformat(venta['fecha']).strftime('%d/%m/%Y %H:%M')
            self.ventas_tree.insert('', 'end', values=(
                venta['id'],
                fecha,
                venta['cliente']['nombre'],
                f"Q{venta['total']:.2f}"
            ))
    
    def ver_detalle_venta(self):
        seleccion = self.ventas_tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione una venta")
            return
            
        venta_id = self.ventas_tree.item(seleccion[0])['values'][0]
        venta = next((v for v in self.ventas if v['id'] == venta_id), None)
        
        if venta:
            self.imprimir_factura(venta)
    
    def exportar_ventas(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        if not filename:
            return
            
        try:
            if filename.endswith('.csv'):
                import csv
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Fecha', 'Cliente', 'NIT', 'Método Pago', 'Productos', 'Total'])
                    for venta in self.ventas:
                        productos = "; ".join(
                            f"{p['cantidad']}x {p['producto']} (Q{p['precio']:.2f})" 
                            for p in venta['productos']
                        )
                        writer.writerow([
                            venta['id'],
                            datetime.fromisoformat(venta['fecha']).strftime('%d/%m/%Y %H:%M'),
                            venta['cliente']['nombre'],
                            venta['cliente']['nit'],
                            venta['cliente']['metodo_pago'],
                            productos,
                            f"Q{venta['total']:.2f}"
                        ])
            else:
                with open(filename, 'w') as f:
                    json.dump(self.ventas, f, indent=4)
            
            messagebox.showinfo("Éxito", "Ventas exportadas correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")
    
    def run(self):
        self.window.mainloop()

class MenuProductos:
    def __init__(self, root, inventario, callback_seleccion=None):
        self.root = root
        self.inventario = inventario
        self.callback_seleccion = callback_seleccion
        
        self.window = tk.Toplevel(root)
        self.window.title("Menú de Productos")
        self.window.geometry("800x600")
        
        # Configurar estilo
        self.conf_estilo()
        
        # Interfaz
        self.conf_gui()
        
        # Cargar datos iniciales
        self.actualizar_tabla()
    
    def conf_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        PRIMARY_COLOR = "#4a90e2"
        SECONDARY_COLOR = "#2c3e50"
        BG_COLOR = "#f5f6fa"
        
        style.configure(".", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=SECONDARY_COLOR)
        style.configure("TButton", background=PRIMARY_COLOR, foreground="white")
        style.configure("Treeview", fieldbackground=BG_COLOR, background=BG_COLOR)
        style.configure("Treeview.Heading", background=PRIMARY_COLOR, foreground="white")
    
    def conf_gui(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Barra de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', padx=5, fill='x', expand=True)
        search_entry.bind('<KeyRelease>', self.filtrar_productos)
        
        # Tabla de productos
        columns = ('producto', 'precio', 'stock')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        self.tree.heading('producto', text='Producto')
        self.tree.heading('precio', text='Precio (Q)')
        self.tree.heading('stock', text='Stock Disponible')
        
        self.tree.column('producto', width=400)
        self.tree.column('precio', width=200, anchor='e')
        self.tree.column('stock', width=200, anchor='e')
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Si hay callback de selección, configuramos doble click
        if self.callback_seleccion:
            self.tree.bind('<Double-1>', self.seleccionar_producto)
        
        # Botón de actualizar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Actualizar", command=self.actualizar_tabla).pack(side='right', padx=5)
    
    def actualizar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for producto, precio in self.inventario.productos.items():
            stock = self.inventario.stock.get(producto, 0)
            self.tree.insert('', 'end', values=(
                producto, 
                f"Q{precio:.2f}", 
                stock
            ))
    
    def filtrar_productos(self, event=None):
        query = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            producto = values[0].lower()
            
            if query in producto:
                self.tree.item(item, tags=('visible',))
            else:
                self.tree.item(item, tags=('hidden',))
        
        self.tree.tag_configure('visible', display='')
        self.tree.tag_configure('hidden', display='none')
    
    def seleccionar_producto(self, event):
        item = self.tree.selection()[0]
        producto = self.tree.item(item)['values'][0]
        
        if self.callback_seleccion:
            self.callback_seleccion(producto)
            self.window.destroy()
    
    def show(self):
        self.window.grab_set()
        self.window.wait_window()

def iniciar_modulo_ventas(root=None, inventario=None):
    # Verificar si ya está abierto
    for widget in root.winfo_children() if root else []:
        if isinstance(widget, tk.Toplevel) and widget.title() == "Sistema de Ventas - Textiles Rosy":
            widget.lift()
            return None
    app = VentasTextiles(root, inventario)
    return app

if __name__ == "__main__":
    app = VentasTextiles()
    app.run()