import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter.font import Font

class Producto:
    def __init__(self, id, nombre, precio, stock, categoria, fecha_actualizacion):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.categoria = categoria
        self.fecha_actualizacion = fecha_actualizacion

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': float(self.precio),
            'stock': int(self.stock),
            'categoria': self.categoria,
            'fecha_actualizacion': self.fecha_actualizacion
        }

class InventarioManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.archivo = "inventario.json"
            cls._instance.cargar_inventario()
        return cls._instance
    
    def cargar_inventario(self):
        try:
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.productos = [Producto(**p) for p in data]
            else:
                self.productos = []
                self.guardar_inventario()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el inventario:\n{str(e)}")
            self.productos = []
    
    def guardar_inventario(self):
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump([p.to_dict() for p in self.productos], f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el inventario:\n{str(e)}")
            return False
    
    def actualizar_producto(self, producto_actualizado):
        for i, p in enumerate(self.productos):
            if p.id == producto_actualizado['id']:
                self.productos[i] = Producto(**producto_actualizado)
                return self.guardar_inventario()
        return False
    
    def eliminar_producto(self, producto_id):
        self.productos = [p for p in self.productos if p.id != producto_id]
        return self.guardar_inventario()
    
    def agregar_producto(self, nuevo_producto):
        self.productos.append(Producto(**nuevo_producto))
        return self.guardar_inventario()
    
    def actualizar_stock(self, producto_id, cantidad):
        for producto in self.productos:
            if producto.id == producto_id:
                nuevo_stock = producto.stock + cantidad
                if nuevo_stock < 0:
                    return False
                producto.stock = nuevo_stock
                producto.fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M")
                return self.guardar_inventario()
        return False

class SistemaInventario:
    def __init__(self):
        self.manager = InventarioManager()
        self.categorias = ["Guipiles", "Cortes", "Fajas", "Accesorios", "Otros"]
        self.producto_editando = None
        
        self.window = tk.Tk()
        self.window.title("Sistema de Inventario - Textiles Rosy")
        self.window.geometry("1200x750")
        self.window.minsize(1000, 650)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.configurar_estilos()
        self.setup_ui()
        self.actualizar_datos()
        self.actualizar_tabla()
        
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
        
        style.configure("Treeview", 
                       background="#ffffff",
                       fieldbackground="#ffffff",
                       foreground="#000000")
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding=(15, 15))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = ttk.Frame(main_frame, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        form_frame = ttk.LabelFrame(left_frame, text="Gestión de Productos", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(form_frame, text="Nombre del Producto:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var, font=self.font_normal).grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(form_frame, text="Precio (Q):").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.precio_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.precio_var, font=self.font_normal).grid(row=3, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(form_frame, text="Stock Disponible:").grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.stock_var = tk.IntVar(value=0)
        ttk.Spinbox(form_frame, from_=0, to=1000, textvariable=self.stock_var, 
                   font=self.font_normal, width=10).grid(row=5, column=0, sticky="w", pady=(0, 10))
        
        ttk.Label(form_frame, text="Categoría:").grid(row=6, column=0, sticky="w", pady=(0, 5))
        self.categoria_var = tk.StringVar()
        self.categoria_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.categoria_var, 
            values=self.categorias, 
            state="readonly",
            font=self.font_normal
        )
        self.categoria_combo.grid(row=7, column=0, sticky="ew", pady=(0, 15))
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=8, column=0, sticky="ew")
        
        self.btn_guardar = ttk.Button(btn_frame, text="Guardar", command=self.guardar_producto, 
                                    style="Accent.TButton")
        self.btn_guardar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.btn_limpiar = ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario)
        self.btn_limpiar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.btn_eliminar = ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_producto,
                                     style="Danger.TButton")
        self.btn_eliminar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        actions_frame = ttk.LabelFrame(left_frame, text="Acciones Rápidas", padding=15)
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(actions_frame, text="Exportar Inventario", command=self.exportar_inventario).pack(fill=tk.X, pady=5)
        ttk.Button(actions_frame, text="Importar Inventario", command=self.importar_inventario).pack(fill=tk.X, pady=5)
        ttk.Button(actions_frame, text="Actualizar Stock", command=self.actualizar_stock_masivo).pack(fill=tk.X, pady=5)
        
        stats_frame = ttk.LabelFrame(left_frame, text="Estadísticas", padding=15)
        stats_frame.pack(fill=tk.X)
        
        self.total_var = tk.StringVar(value="Total productos: 0")
        ttk.Label(stats_frame, textvariable=self.total_var, font=self.font_bold).pack(anchor="w")
        
        self.stock_bajo_var = tk.StringVar(value="Productos con stock bajo: 0")
        ttk.Label(stats_frame, textvariable=self.stock_bajo_var, font=self.font_bold).pack(anchor="w")
        
        self.sin_stock_var = tk.StringVar(value="Productos agotados: 0")
        ttk.Label(stats_frame, textvariable=self.sin_stock_var, font=self.font_bold).pack(anchor="w")
        
        table_frame = ttk.LabelFrame(right_frame, text="Inventario Actual", padding=15)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "nombre", "precio", "stock", "categoria", "fecha")
        self.tabla = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings",
            selectmode="extended"
        )
        
        self.tabla.heading("id", text="ID", anchor=tk.CENTER)
        self.tabla.heading("nombre", text="Nombre del Producto", anchor=tk.W)
        self.tabla.heading("precio", text="Precio (Q)", anchor=tk.E)
        self.tabla.heading("stock", text="Stock", anchor=tk.CENTER)
        self.tabla.heading("categoria", text="Categoría", anchor=tk.W)
        self.tabla.heading("fecha", text="Última Actualización", anchor=tk.W)
        
        self.tabla.column("id", width=80, anchor=tk.CENTER, stretch=False)
        self.tabla.column("nombre", width=250, anchor=tk.W, stretch=True)
        self.tabla.column("precio", width=120, anchor=tk.E, stretch=False)
        self.tabla.column("stock", width=80, anchor=tk.CENTER, stretch=False)
        self.tabla.column("categoria", width=150, anchor=tk.W, stretch=False)
        self.tabla.column("fecha", width=180, anchor=tk.W, stretch=False)
        
        y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tabla.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.tabla.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.tabla.bind("<<TreeviewSelect>>", self.cargar_producto_seleccionado)
        self.tabla.bind("<Double-1>", self.editar_producto_doble_click)
        
        for col in columns:
            self.tabla.heading(col, command=lambda c=col: self.ordenar_por_columna(c))

    def ordenar_por_columna(self, col):
        items = [(self.tabla.set(child, col), child) for child in self.tabla.get_children('')]
        
        try:
            items.sort(key=lambda x: float(x[0]) if col in ["precio", "stock"] else x[0])
        except ValueError:
            items.sort()
        
        for index, (val, child) in enumerate(items):
            self.tabla.move(child, '', index)

    def actualizar_datos(self):
        self.productos = self.manager.productos

    def actualizar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        
        for producto in sorted(self.productos, key=lambda x: x.nombre.lower()):
            tags = []
            if producto.stock == 0:
                tags.append('agotado')
            elif producto.stock < 5:
                tags.append('bajo_stock')
            
            self.tabla.insert("", "end", 
                            values=(
                                producto.id,
                                producto.nombre,
                                f"{producto.precio:.2f}",
                                producto.stock,
                                producto.categoria,
                                producto.fecha_actualizacion
                            ),
                            tags=tuple(tags))
        
        self.tabla.tag_configure('agotado', background='#FFCDD2', foreground='#D32F2F')
        self.tabla.tag_configure('bajo_stock', background='#FFF3E0', foreground='#E65100')
        
        self.actualizar_estadisticas()

    def actualizar_estadisticas(self):
        total = len(self.productos)
        stock_bajo = sum(1 for p in self.productos if 0 < p.stock < 5)
        sin_stock = sum(1 for p in self.productos if p.stock == 0)
        
        self.total_var.set(f"Total productos: {total}")
        self.stock_bajo_var.set(f"Productos con stock bajo: {stock_bajo}")
        self.sin_stock_var.set(f"Productos agotados: {sin_stock}")

    def cargar_producto_seleccionado(self, event=None):
        seleccion = self.tabla.selection()
        if not seleccion or len(seleccion) > 1:
            self.limpiar_formulario()
            return
        
        item = self.tabla.item(seleccion[0])
        producto_id = item['values'][0]
        
        for producto in self.productos:
            if producto.id == producto_id:
                self.producto_editando = producto
                self.nombre_var.set(producto.nombre)
                self.precio_var.set(producto.precio)
                self.stock_var.set(producto.stock)
                self.categoria_var.set(producto.categoria)
                self.btn_guardar.config(text="Actualizar")
                break

    def editar_producto_doble_click(self, event):
        self.cargar_producto_seleccionado()

    def guardar_producto(self):
        nombre = self.nombre_var.get().strip()
        precio = self.precio_var.get()
        stock = self.stock_var.get()
        categoria = self.categoria_var.get()
        
        if not nombre:
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre para el producto")
            return
        
        if precio <= 0:
            messagebox.showwarning("Advertencia", "El precio debe ser mayor que cero")
            return
        
        if stock < 0:
            messagebox.showwarning("Advertencia", "El stock no puede ser negativo")
            return
        
        if not categoria:
            messagebox.showwarning("Advertencia", "Debe seleccionar una categoría")
            return
        
        if self.producto_editando:
            # Verificar si el nombre ya existe (excluyendo el producto actual)
            if any(p.nombre.lower() == nombre.lower() and p.id != self.producto_editando.id for p in self.productos):
                messagebox.showwarning("Advertencia", "Ya existe un producto con ese nombre")
                return
                
            producto_actualizado = {
                'id': self.producto_editando.id,
                'nombre': nombre,
                'precio': precio,
                'stock': stock,
                'categoria': categoria,
                'fecha_actualizacion': datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
            if self.manager.actualizar_producto(producto_actualizado):
                self.actualizar_datos()
                self.actualizar_tabla()
                self.limpiar_formulario()
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
        else:
            # Verificar si el nombre ya existe
            if any(p.nombre.lower() == nombre.lower() for p in self.productos):
                messagebox.showwarning("Advertencia", "Ya existe un producto con ese nombre")
                return
                
            nuevo_producto = {
                'id': str(datetime.now().timestamp()).replace('.', '')[-8:],
                'nombre': nombre,
                'precio': precio,
                'stock': stock,
                'categoria': categoria,
                'fecha_actualizacion': datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
            if self.manager.agregar_producto(nuevo_producto):
                self.actualizar_datos()
                self.actualizar_tabla()
                self.limpiar_formulario()
                messagebox.showinfo("Éxito", "Producto agregado correctamente")

    def eliminar_producto(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione al menos un producto para eliminar")
            return
        
        productos_a_eliminar = []
        nombres_productos = []
        
        for item_id in seleccion:
            item = self.tabla.item(item_id)
            producto_id = item['values'][0]
            producto_nombre = item['values'][1]
            
            for producto in self.productos:
                if producto.id == producto_id:
                    productos_a_eliminar.append(producto)
                    nombres_productos.append(producto_nombre)
                    break
        
        confirmacion = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Está seguro de eliminar los siguientes productos?\n\n" + 
            "\n".join(f"- {nombre}" for nombre in nombres_productos)
        )
        
        if not confirmacion:
            return
        
        for producto in productos_a_eliminar:
            if self.manager.eliminar_producto(producto.id):
                self.actualizar_datos()
        
        self.actualizar_tabla()
        self.limpiar_formulario()
        messagebox.showinfo("Éxito", f"{len(productos_a_eliminar)} productos eliminados correctamente")

    def limpiar_formulario(self):
        self.producto_editando = None
        self.nombre_var.set("")
        self.precio_var.set(0)
        self.stock_var.set(0)
        self.categoria_var.set("")
        self.btn_guardar.config(text="Guardar")
        self.tabla.selection_remove(self.tabla.selection())

    def exportar_inventario(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Exportar inventario como..."
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([p.to_dict() for p in self.productos], f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", "Inventario exportado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el inventario:\n{str(e)}")

    def importar_inventario(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Seleccionar archivo para importar"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                raise ValueError("Formato de archivo inválido")
                
            productos_validos = []
            for item in data:
                try:
                    if not all(key in item for key in ['id', 'nombre', 'precio', 'stock', 'categoria', 'fecha_actualizacion']):
                        continue
                    
                    productos_validos.append(item)
                except Exception:
                    continue
            
            if not productos_validos:
                raise ValueError("No se encontraron productos válidos en el archivo")
            
            confirmacion = messagebox.askyesno(
                "Confirmar Importación", 
                f"Se importarán {len(productos_validos)} productos.\n\n" +
                "¿Desea reemplazar el inventario actual o agregar estos productos?"
            )
            
            if confirmacion:
                self.manager.productos = [Producto(**p) for p in productos_validos]
            else:
                ids_existentes = {p.id for p in self.manager.productos}
                for p in productos_validos:
                    if p['id'] not in ids_existentes:
                        self.manager.productos.append(Producto(**p))
            
            if self.manager.guardar_inventario():
                self.actualizar_datos()
                self.actualizar_tabla()
                messagebox.showinfo("Éxito", f"Se importaron {len(productos_validos)} productos correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo importar el inventario:\n{str(e)}")

    def actualizar_stock_masivo(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione al menos un producto")
            return
        
        cantidad = simpledialog.askinteger(
            "Actualizar Stock", 
            "Ingrese la cantidad a agregar (use negativo para restar):",
            parent=self.window
        )
        
        if cantidad is None:
            return
        
        productos_actualizados = 0
        productos_no_actualizados = []
        
        for item_id in seleccion:
            item = self.tabla.item(item_id)
            producto_id = item['values'][0]
            producto_nombre = item['values'][1]
            
            if self.manager.actualizar_stock(producto_id, cantidad):
                productos_actualizados += 1
            else:
                productos_no_actualizados.append(producto_nombre)
        
        if productos_no_actualizados:
            messagebox.showwarning("Advertencia", 
                f"No se pudo actualizar stock para:\n{', '.join(productos_no_actualizados)}\nVerifique que no quede stock negativo")
        
        if productos_actualizados > 0:
            self.actualizar_datos()
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", f"Stock actualizado para {productos_actualizados} productos")

    def on_close(self):
        if messagebox.askokcancel("Salir", "¿Desea salir del sistema de inventario?"):
            self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = SistemaInventario()
    app.run()