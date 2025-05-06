import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

class InventarioTextiles:
    def __init__(self, root=None):
        self.root = root
        self.window = tk.Toplevel(root) if root else tk.Tk()
        self.window.title("Sistema de Inventario - Textiles Rosy")
        self.window.geometry("1000x600")
        
        # Control para evitar múltiples instancias
        self.window.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        
        # Configuración de archivos
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.stock_file = os.path.join(self.data_dir, "stock.json")
        self.precios_file = os.path.join(self.data_dir, "precios.json")
        
        # Cargar datos
        self.cargar_datos()
        
        # Configurar interfaz
        self.conf_estilo()
        self.conf_gui()
        
    def cargar_datos(self):
        """Carga los datos de productos y stock"""
        self.productos = self.cargar_productos()
        self.stock = self.cargar_stock()
    
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
        
    def cargar_productos(self):
        productos_base = {
            # ... (todos tus productos aquí)
            "Marcador fino": 1200
        }
        
        if os.path.exists(self.precios_file):
            try:
                with open(self.precios_file, 'r') as f:
                    return json.load(f)
            except:
                return productos_base
        return productos_base
    
    def cargar_stock(self):
        stock_base = {producto: 0 for producto in self.productos.keys()}
        
        if os.path.exists(self.stock_file):
            try:
                with open(self.stock_file, 'r') as f:
                    data = json.load(f)
                    return {**stock_base, **data}
            except:
                return stock_base
        return stock_base
    
    def guardar_datos(self):
        with open(self.stock_file, 'w') as f:
            json.dump(self.stock, f, indent=4)
        with open(self.precios_file, 'w') as f:
            json.dump(self.productos, f, indent=4)
    
    def conf_gui(self):
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Panel de controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=5)
        
        # Combobox para selección de productos
        ttk.Label(control_frame, text="Producto:").pack(side='left', padx=5)
        self.producto_var = tk.StringVar()
        self.producto_cb = ttk.Combobox(control_frame, textvariable=self.producto_var, 
                                      values=list(self.productos.keys()), state='readonly')
        self.producto_cb.pack(side='left', padx=5)
        self.producto_cb.bind('<<ComboboxSelected>>', self.actualizar_campos)
        
        # Precio
        ttk.Label(control_frame, text="Precio:").pack(side='left', padx=5)
        self.precio_var = tk.DoubleVar()
        ttk.Entry(control_frame, textvariable=self.precio_var, width=10).pack(side='left', padx=5)
        
        # Stock
        ttk.Label(control_frame, text="Stock:").pack(side='left', padx=5)
        self.stock_var = tk.IntVar()
        ttk.Entry(control_frame, textvariable=self.stock_var, width=10).pack(side='left', padx=5)
        
        # Botones
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="Actualizar", command=self.actualizar_producto).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Nuevo", command=self.nuevo_producto).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_producto).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Refrescar", command=self.refrescar_datos).pack(side='left', padx=2)
        
        # Treeview para mostrar inventario
        columns = ('producto', 'precio', 'stock')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        self.tree.heading('producto', text='Producto')
        self.tree.heading('precio', text='Precio (Q)')
        self.tree.heading('stock', text='Stock')
        
        self.tree.column('producto', width=400)
        self.tree.column('precio', width=200, anchor='e')
        self.tree.column('stock', width=200, anchor='e')
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botones de exportación
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill='x', pady=5)
        
        ttk.Button(export_frame, text="Exportar a JSON", command=self.exportar_json).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Exportar a CSV", command=self.exportar_csv).pack(side='left', padx=5)
        
        # Cargar datos iniciales
        self.actualizar_tabla()
    
    def refrescar_datos(self):
        """Recarga los datos desde los archivos y actualiza la interfaz"""
        self.cargar_datos()
        self.producto_cb['values'] = list(self.productos.keys())
        self.actualizar_tabla()
        messagebox.showinfo("Actualizado", "Datos refrescados correctamente")
    
    def actualizar_campos(self, event=None):
        producto = self.producto_var.get()
        if producto:
            self.precio_var.set(self.productos[producto])
            self.stock_var.set(self.stock.get(producto, 0))
    
    def actualizar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for producto, precio in self.productos.items():
            stock = self.stock.get(producto, 0)
            self.tree.insert('', 'end', values=(producto, f"Q{precio:.2f}", stock))
    
    def actualizar_producto(self):
        producto = self.producto_var.get()
        if not producto:
            messagebox.showwarning("Error", "Seleccione un producto")
            return
            
        try:
            nuevo_precio = float(self.precio_var.get())
            nuevo_stock = int(self.stock_var.get())
            
            if nuevo_precio <= 0 or nuevo_stock < 0:
                raise ValueError("Valores inválidos")
                
            self.productos[producto] = nuevo_precio
            self.stock[producto] = nuevo_stock
            self.guardar_datos()
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
    
    def nuevo_producto(self):
        def guardar_nuevo():
            nombre = nombre_var.get().strip()
            try:
                precio = float(precio_var.get())
                stock = int(stock_var.get())
                
                if not nombre or precio <= 0 or stock < 0:
                    raise ValueError("Datos inválidos")
                    
                if nombre in self.productos:
                    raise ValueError("El producto ya existe")
                    
                self.productos[nombre] = precio
                self.stock[nombre] = stock
                self.guardar_datos()
                self.refrescar_datos()
                top.destroy()
                messagebox.showinfo("Éxito", "Producto agregado correctamente")
                
            except ValueError as e:
                messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        
        top = tk.Toplevel(self.window)
        top.title("Nuevo Producto")
        
        ttk.Label(top, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_var = tk.StringVar()
        ttk.Entry(top, textvariable=nombre_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Precio:").grid(row=1, column=0, padx=5, pady=5)
        precio_var = tk.StringVar()
        ttk.Entry(top, textvariable=precio_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Stock inicial:").grid(row=2, column=0, padx=5, pady=5)
        stock_var = tk.StringVar(value="0")
        ttk.Entry(top, textvariable=stock_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(top, text="Guardar", command=guardar_nuevo).grid(row=3, column=0, columnspan=2, pady=10)
    
    def eliminar_producto(self):
        producto = self.producto_var.get()
        if not producto:
            messagebox.showwarning("Error", "Seleccione un producto")
            return
            
        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto {producto}?"):
            del self.productos[producto]
            del self.stock[producto]
            self.guardar_datos()
            self.refrescar_datos()
            self.producto_var.set('')
            self.precio_var.set(0)
            self.stock_var.set(0)
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
    
    def exportar_json(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                data = {
                    'productos': self.productos,
                    'stock': self.stock,
                    'fecha_exportacion': datetime.now().isoformat()
                }
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Éxito", "Datos exportados a JSON correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")
    
    def exportar_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            try:
                import csv
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Producto', 'Precio', 'Stock'])
                    for producto, precio in self.productos.items():
                        stock = self.stock.get(producto, 0)
                        writer.writerow([producto, precio, stock])
                messagebox.showinfo("Éxito", "Datos exportados a CSV correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")
    
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

def iniciar_modulo_inventario(root=None):
    # Verificar si ya está abierto
    for widget in root.winfo_children() if root else []:
        if isinstance(widget, tk.Toplevel) and widget.title() == "Sistema de Inventario - Textiles Rosy":
            widget.lift()
            return None
    app = InventarioTextiles(root)
    return app

if __name__ == "__main__":
    app = InventarioTextiles()
    app.run()