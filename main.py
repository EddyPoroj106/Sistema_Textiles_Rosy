import tkinter as tk
from tkinter import ttk, messagebox
from inventario_textiles import InventarioTextiles
from ventas_textiles import VentasTextiles

class TextilesRosy:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Textiles Rosy")
        self.root.geometry("400x300")
        
        self.modulo_inventario = None
        self.modulo_ventas = None
        
        self.conf_estilo()
        self.conf_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
    
    def conf_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background="#f5f6fa")
        style.configure("TButton", background="#4a90e2", foreground="white", padding=10)
    
    def conf_gui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Textiles Rosy", font=('Arial', 18, 'bold')).pack(pady=20)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="Módulo de Inventario", 
                 command=self.abrir_inventario).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Módulo de Ventas", 
                 command=self.abrir_ventas).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Salir", 
                 command=self.cerrar_aplicacion).pack(fill='x', pady=5)
    
    def abrir_inventario(self):
        if self.modulo_inventario is None or not self.modulo_inventario.window.winfo_exists():
            self.modulo_inventario = InventarioTextiles(self.root)
            # Si ventas está abierto, actualizar su referencia al inventario
            if self.modulo_ventas and self.modulo_ventas.window.winfo_exists():
                self.modulo_ventas.inventario = self.modulo_inventario
                self.modulo_ventas.refrescar_datos()
        else:
            self.modulo_inventario.window.lift()
    
    def abrir_ventas(self):
        if self.modulo_ventas is None or not self.modulo_ventas.window.winfo_exists():
            # Pasar None si el inventario no está abierto
            inventario_ref = self.modulo_inventario if self.modulo_inventario else None
            self.modulo_ventas = VentasTextiles(self.root, inventario_ref)
            
            # Configurar para ocultar panel de productos si no hay inventario
            if inventario_ref is None:
                self.ocultar_panel_productos()
        else:
            self.modulo_ventas.window.lift()
    
    def ocultar_panel_productos(self):
        """Oculta el panel de productos en el módulo de ventas"""
        if hasattr(self.modulo_ventas, 'productos_frame'):
            self.modulo_ventas.productos_frame.pack_forget()
            # Ajustar el tamaño de la ventana
            self.modulo_ventas.window.geometry("900x800")
    
    def cerrar_modulo(self, modulo):
        if modulo == 'inventario' and self.modulo_inventario:
            self.modulo_inventario.cerrar_ventana()
            self.modulo_inventario = None
    
    def cerrar_aplicacion(self):
        if self.modulo_inventario:
            self.modulo_inventario.cerrar_ventana()
        if self.modulo_ventas:
            self.modulo_ventas.cerrar_ventana()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TextilesRosy()
    app.run()