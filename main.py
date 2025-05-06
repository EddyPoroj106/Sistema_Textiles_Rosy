import tkinter as tk
from tkinter import ttk, messagebox
from inventario_textiles import InventarioTextiles
from ventas_textiles import VentasTextiles
from recursos_humanos import RecursosHumanos
from finanzas_textiles import FinanzasTextiles

class TextilesRosy:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Integral - Textiles Rosy")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        
        # Inicializar módulos (aún no instanciados)
        self.modulo_inventario = None
        self.modulo_ventas = None
        self.modulo_rrhh = None
        self.modulo_finanzas = None
        
        # Configurar estilo
        self.conf_estilo()
        
        # Interfaz principal
        self.conf_gui()
        
        # Control de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
    
    def conf_estilo(self):
        """Configura el estilo visual para toda la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores corporativos
        style.configure(".", background="#f5f6fa", foreground="#2c3e50")
        style.configure("TButton", 
                      background="#3498db", 
                      foreground="white", 
                      font=('Arial', 10, 'bold'),
                      padding=10)
        style.configure("Title.TLabel", 
                      font=('Arial', 16, 'bold'), 
                      foreground="#2c3e50")
    
    def conf_gui(self):
        """Configura la interfaz gráfica principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Encabezado
        ttk.Label(main_frame, 
                 text="Textiles Rosy", 
                 style="Title.TLabel").pack(pady=20)
        
        # Botones de módulos
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(expand=True)
        
        ttk.Button(btn_frame, 
                  text="📦 Módulo de Inventario",
                  command=self.abrir_inventario).pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, 
                  text="💰 Módulo de Ventas",
                  command=self.abrir_ventas).pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, 
                  text="👥 Módulo de RRHH",
                  command=self.abrir_rrhh).pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, 
                  text="📊 Módulo de Finanzas",
                  command=self.abrir_finanzas).pack(fill='x', pady=5)
        
        # Separador
        ttk.Separator(main_frame).pack(fill='x', pady=10)
        
        # Botón de salida
        ttk.Button(main_frame, 
                  text="Salir del Sistema",
                  command=self.cerrar_aplicacion,
                  style="Accent.TButton").pack(fill='x')
    
    def abrir_inventario(self):
        """Abre el módulo de inventario"""
        if self.modulo_inventario is None or not self.modulo_inventario.window.winfo_exists():
            self.modulo_inventario = InventarioTextiles(self.root)
            
            # Actualizar referencias en otros módulos
            if self.modulo_ventas:
                self.modulo_ventas.inventario = self.modulo_inventario
            if self.modulo_finanzas:
                self.modulo_finanzas.modulo_inventario = self.modulo_inventario
    
    def abrir_ventas(self):
        """Abre el módulo de ventas"""
        if self.modulo_ventas is None or not self.modulo_ventas.window.winfo_exists():
            inventario_ref = self.modulo_inventario if self.modulo_inventario else None
            self.modulo_ventas = VentasTextiles(self.root, inventario_ref)
            
            # Actualizar referencia en finanzas
            if self.modulo_finanzas:
                self.modulo_finanzas.modulo_ventas = self.modulo_ventas
    
    def abrir_rrhh(self):
        """Abre el módulo de recursos humanos"""
        if self.modulo_rrhh is None or not self.modulo_rrhh.window.winfo_exists():
            self.modulo_rrhh = RecursosHumanos(self.root)
            
            # Actualizar referencia en finanzas
            if self.modulo_finanzas:
                self.modulo_finanzas.modulo_rrhh = self.modulo_rrhh
    
    def abrir_finanzas(self):
        """Abre el módulo de finanzas"""
        if self.modulo_finanzas is None or not self.modulo_finanzas.window.winfo_exists():
            self.modulo_finanzas = FinanzasTextiles(
                self.root,
                ventas=self.modulo_ventas,
                inventario=self.modulo_inventario,
                rrhh=self.modulo_rrhh
            )
    
    def cerrar_aplicacion(self):
        """Maneja el cierre ordenado de toda la aplicación"""
        # Cerrar módulos en orden específico
        modulos = [
            self.modulo_finanzas,
            self.modulo_rrhh,
            self.modulo_ventas,
            self.modulo_inventario
        ]
        
        for modulo in modulos:
            if modulo and hasattr(modulo, 'window'):
                try:
                    modulo.window.destroy()
                except:
                    pass
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TextilesRosy()
    app.run()