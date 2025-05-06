import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter.font import Font
from inventario import InventarioManager, Producto

class ProductoVenta:
    def __init__(self, id, nombre, precio, cantidad=1):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad
    
    def subtotal(self):
        return self.precio * self.cantidad

class SistemaVentas:
    def __init__(self):
        self.manager = InventarioManager()
        self.archivo_tickets = "tickets_ventas.json"
        self.carrito = []
        self.max_cantidad = 100
        
        self.window = tk.Tk()
        self.window.title("Sistema de Ventas - Textiles Rosy")
        self.window.geometry("1200x750")
        self.window.minsize(1000, 650)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.configurar_estilos()
        self.setup_ui()
        self.cargar_inventario()
    
    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        self.font_title = Font(family='Helvetica', size=12, weight='bold')
        self.font_normal = Font(family='Helvetica', size=10)
        self.font_bold = Font(family='Helvetica', size=10, weight='bold')
        
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=self.font_normal)
        style.configure("TButton", font=self.font_normal)
        style.configure("Treeview", font=self.font_normal, rowheight=28)
        style.configure("Treeview.Heading", font=self.font_bold)
        
        style.configure("Accent.TButton", foreground="white", background="#4CAF50", font=self.font_bold)
        style.configure("Danger.TButton", foreground="white", background="#F44336", font=self.font_bold)
        style.configure("Primary.TButton", foreground="white", background="#2196F3", font=self.font_bold)
        
        style.configure("Treeview", 
                      background="#ffffff",
                      fieldbackground="#ffffff",
                      foreground="#000000")
        
        style.map('Treeview',
                 background=[('selected', '#347083')],
                 foreground=[('selected', 'white')])
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding=(15, 15))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo (productos)
        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Panel derecho (carrito)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # ========== LISTA DE PRODUCTOS ==========
        products_frame = ttk.LabelFrame(left_frame, text="Productos Disponibles", padding=15)
        products_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Filtros
        filter_frame = ttk.Frame(products_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", self.filtrar_productos)
        ttk.Entry(filter_frame, textvariable=self.busqueda_var, width=25).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(filter_frame, text="Categoría:").pack(side=tk.LEFT, padx=(0, 5))
        self.categoria_filtro_var = tk.StringVar()
        self.categoria_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.categoria_filtro_var, 
            values=["Todas"],
            state="readonly",
            width=15
        )
        self.categoria_combo.pack(side=tk.LEFT)
        self.categoria_combo.bind("<<ComboboxSelected>>", lambda e: self.filtrar_productos())
        
        # Treeview de productos
        self.productos_tree = ttk.Treeview(
            products_frame,
            columns=("id", "precio", "stock", "categoria"),
            show="headings",
            selectmode="browse",
            height=15
        )
        
        self.productos_tree.heading("id", text="ID", anchor=tk.CENTER)
        self.productos_tree.heading("precio", text="Precio (Q)", anchor=tk.E)
        self.productos_tree.heading("stock", text="Stock", anchor=tk.CENTER)
        self.productos_tree.heading("categoria", text="Categoría", anchor=tk.W)
        
        self.productos_tree.column("id", width=80, anchor=tk.CENTER, stretch=False)
        self.productos_tree.column("precio", width=100, anchor=tk.E, stretch=False)
        self.productos_tree.column("stock", width=80, anchor=tk.CENTER, stretch=False)
        self.productos_tree.column("categoria", width=120, anchor=tk.W, stretch=False)
        
        scroll_y = ttk.Scrollbar(products_frame, orient=tk.VERTICAL, command=self.productos_tree.yview)
        scroll_x = ttk.Scrollbar(products_frame, orient=tk.HORIZONTAL, command=self.productos_tree.xview)
        self.productos_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.productos_tree.pack(fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Controles de cantidad
        control_frame = ttk.Frame(products_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(control_frame, text="Cantidad:").pack(side=tk.LEFT, padx=(0, 5))
        self.cantidad_var = tk.IntVar(value=1)
        self.spinbox_cantidad = ttk.Spinbox(
            control_frame, 
            from_=1, 
            to=self.max_cantidad,
            textvariable=self.cantidad_var,
            width=5,
            command=self.actualizar_spinbox_max
        )
        self.spinbox_cantidad.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            control_frame, 
            text="Agregar al Carrito", 
            command=self.agregar_al_carrito,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT)
        
        # ========== CARRITO DE COMPRAS ==========
        cart_frame = ttk.LabelFrame(right_frame, text="Carrito de Compras", padding=15)
        cart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview del carrito
        self.carrito_tree = ttk.Treeview(
            cart_frame,
            columns=("precio_unit", "subtotal"),
            show="headings",
            selectmode="extended",
            height=15
        )
        
        self.carrito_tree.heading("#0", text="Producto", anchor=tk.W)
        self.carrito_tree.heading("precio_unit", text="Precio Unit.", anchor=tk.E)
        self.carrito_tree.heading("subtotal", text="Subtotal", anchor=tk.E)
        
        self.carrito_tree.column("#0", width=300, anchor=tk.W, stretch=True)
        self.carrito_tree.column("precio_unit", width=120, anchor=tk.E, stretch=False)
        self.carrito_tree.column("subtotal", width=120, anchor=tk.E, stretch=False)
        
        scroll_y_cart = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.carrito_tree.yview)
        scroll_x_cart = ttk.Scrollbar(cart_frame, orient=tk.HORIZONTAL, command=self.carrito_tree.xview)
        self.carrito_tree.configure(yscrollcommand=scroll_y_cart.set, xscrollcommand=scroll_x_cart.set)
        
        self.carrito_tree.pack(fill=tk.BOTH, expand=True)
        scroll_y_cart.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x_cart.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Total y controles
        bottom_frame = ttk.Frame(cart_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.total_var = tk.StringVar(value="Total: Q0.00")
        ttk.Label(
            bottom_frame, 
            textvariable=self.total_var,
            font=self.font_bold
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame,
            text="Eliminar Seleccionados",
            command=self.eliminar_del_carrito,
            style="Danger.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Vaciar Carrito",
            command=self.vaciar_carrito,
            style="Danger.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Finalizar Venta",
            command=self.finalizar_venta,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        # Bind eventos
        self.productos_tree.bind("<Double-1>", lambda e: self.agregar_al_carrito())
        self.carrito_tree.bind("<Delete>", lambda e: self.eliminar_del_carrito())
    
    def actualizar_spinbox_max(self):
        seleccion = self.productos_tree.selection()
        if seleccion:
            item = self.productos_tree.item(seleccion[0])
            stock_disponible = int(item['values'][2])
            self.spinbox_cantidad.config(to=min(stock_disponible, self.max_cantidad))
    
    def get_categorias_inventario(self):
        categorias = set()
        for producto in self.manager.productos:
            categorias.add(producto.categoria)
        return sorted(categorias)
    
    def cargar_inventario(self):
        try:
            self.manager.cargar_inventario()
            categorias = self.get_categorias_inventario()
            self.categoria_combo['values'] = ["Todas"] + categorias
            self.filtrar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el inventario:\n{str(e)}")
    
    def filtrar_productos(self, *args):
        busqueda = self.busqueda_var.get().lower()
        categoria = self.categoria_filtro_var.get()
        
        self.productos_tree.delete(*self.productos_tree.get_children())
        
        for producto in self.manager.productos:
            # Filtrar por búsqueda y categoría
            if (busqueda in producto.nombre.lower() or 
                busqueda in producto.id.lower()) and \
               (categoria == "Todas" or categoria == producto.categoria or not categoria):
                
                tags = []
                if producto.stock <= 0:
                    tags.append('agotado')
                elif producto.stock < 5:
                    tags.append('bajo_stock')
                
                self.productos_tree.insert(
                    "", "end",
                    text=producto.nombre,
                    values=(
                        producto.id,
                        f"{producto.precio:.2f}",
                        producto.stock,
                        producto.categoria
                    ),
                    tags=tuple(tags)
                )
        
        self.productos_tree.tag_configure('agotado', background='#FFCDD2', foreground='#D32F2F')
        self.productos_tree.tag_configure('bajo_stock', background='#FFF3E0', foreground='#E65100')
    
    def agregar_al_carrito(self, event=None):
        seleccion = self.productos_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto primero")
            return
        
        item = self.productos_tree.item(seleccion[0])
        producto_id = item['values'][0]
        nombre = item['text']
        precio = float(item['values'][1])
        stock_disponible = int(item['values'][2])
        cantidad = self.cantidad_var.get()
        
        if stock_disponible <= 0:
            messagebox.showerror("Error", "Este producto está agotado en inventario")
            return
        
        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor que cero")
            return
        
        if cantidad > stock_disponible:
            messagebox.showerror("Error", f"No hay suficiente stock. Disponible: {stock_disponible}")
            return
        
        if cantidad > self.max_cantidad:
            messagebox.showerror("Error", f"No puede comprar más de {self.max_cantidad} unidades del mismo producto")
            return
        
        # Verificar si el producto ya está en el carrito
        for producto in self.carrito:
            if producto.id == producto_id:
                nueva_cantidad = producto.cantidad + cantidad
                if nueva_cantidad > stock_disponible:
                    messagebox.showerror("Error", f"No hay suficiente stock. Disponible: {stock_disponible}")
                    return
                if nueva_cantidad > self.max_cantidad:
                    messagebox.showerror("Error", f"No puede comprar más de {self.max_cantidad} unidades del mismo producto")
                    return
                producto.cantidad = nueva_cantidad
                break
        else:
            # Producto nuevo en el carrito
            self.carrito.append(ProductoVenta(producto_id, nombre, precio, cantidad))
        
        self.actualizar_carrito()
        self.cantidad_var.set(1)  # Resetear cantidad a 1
    
    def actualizar_carrito(self):
        self.carrito_tree.delete(*self.carrito_tree.get_children())
        total = 0.0
        
        for producto in self.carrito:
            self.carrito_tree.insert(
                "", "end",
                text=f"{producto.cantidad}x {producto.nombre}",
                values=(
                    f"Q{producto.precio:.2f}",
                    f"Q{producto.subtotal():.2f}"
                )
            )
            total += producto.subtotal()
        
        self.total_var.set(f"Total: Q{total:.2f}")
    
    def eliminar_del_carrito(self, event=None):
        seleccion = self.carrito_tree.selection()
        if not seleccion:
            return
        
        # Eliminar en orden inverso para evitar problemas con los índices
        for item in reversed(seleccion):
            index = self.carrito_tree.index(item)
            if 0 <= index < len(self.carrito):
                del self.carrito[index]
        
        self.actualizar_carrito()
    
    def vaciar_carrito(self):
        if self.carrito and messagebox.askyesno("Confirmar", "¿Vaciar el carrito?"):
            self.carrito.clear()
            self.actualizar_carrito()
    
    def finalizar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
        
        total = sum(p.subtotal() for p in self.carrito)
        resumen = "\n".join(f"{p.cantidad}x {p.nombre} - Q{p.subtotal():.2f}" for p in self.carrito)
        
        if messagebox.askyesno(
            "Confirmar Venta", 
            f"Resumen de la venta:\n\n{resumen}\n\nTotal: Q{total:.2f}\n\n¿Confirmar venta?"
        ):
            if self.procesar_venta(total):
                messagebox.showinfo("Éxito", "Venta registrada correctamente")
                self.vaciar_carrito()
                self.cargar_inventario()  # Actualizar lista de productos
    
    def procesar_venta(self, total):
        try:
            # Verificar stock antes de actualizar
            productos_sin_stock = []
            
            for producto_carrito in self.carrito:
                producto_encontrado = False
                for producto_inv in self.manager.productos:
                    if producto_inv.id == producto_carrito.id:
                        producto_encontrado = True
                        if producto_inv.stock < producto_carrito.cantidad:
                            productos_sin_stock.append(
                                f"{producto_carrito.nombre} (Stock: {producto_inv.stock}, Pedido: {producto_carrito.cantidad})"
                            )
                        break
                
                if not producto_encontrado:
                    productos_sin_stock.append(f"{producto_carrito.nombre} (Producto no encontrado en inventario)")
            
            if productos_sin_stock:
                messagebox.showerror(
                    "Error en stock", 
                    f"No hay suficiente stock para:\n\n" + "\n".join(productos_sin_stock)
                )
                return False
            
            # Actualizar el stock
            for producto_carrito in self.carrito:
                for producto_inv in self.manager.productos:
                    if producto_inv.id == producto_carrito.id:
                        producto_inv.stock -= producto_carrito.cantidad
                        producto_inv.fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M")
                        break
            
            if not self.manager.guardar_inventario():
                messagebox.showerror("Error", "No se pudo actualizar el inventario")
                return False
            
            # Registrar ticket
            ticket = {
                'fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'productos': [
                    {
                        'id': p.id,
                        'nombre': p.nombre,
                        'precio': p.precio,
                        'cantidad': p.cantidad,
                        'subtotal': p.subtotal()
                    } for p in self.carrito
                ],
                'total': total
            }
            
            tickets = []
            if os.path.exists(self.archivo_tickets):
                with open(self.archivo_tickets, 'r', encoding='utf-8') as f:
                    tickets = json.load(f)
            
            tickets.append(ticket)
            
            with open(self.archivo_tickets, 'w', encoding='utf-8') as f:
                json.dump(tickets, f, indent=4, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo completar la venta:\n{str(e)}")
            return False
    
    def on_close(self):
        if messagebox.askokcancel("Salir", "¿Desea salir del sistema de ventas?"):
            self.window.destroy()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = SistemaVentas()
    app.run()