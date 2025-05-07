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
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        self.root.configure(bg="#ecf0f1")  # Fondo más suave
        self.root.resizable(True, True)
        
        self.modulo_inventario = None
        self.modulo_ventas = None
        self.modulo_rrhh = None
        self.modulo_finanzas = None

        self.conf_estilo()
        self.conf_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def conf_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # General
        style.configure(".", background="#ecf0f1", foreground="#2c3e50", font=('Segoe UI', 10))
        
        # Botón normal
        style.configure("TButton", background="#2980b9", foreground="white", padding=10, font=('Segoe UI', 10, 'bold'))
        style.map("TButton", background=[('active', '#3498db')])

        # Botón especial (salir)
        style.configure("Accent.TButton", background="#c0392b", foreground="white")
        style.map("Accent.TButton", background=[('active', '#e74c3c')])

        # Etiquetas
        style.configure("Title.TLabel", font=('Segoe UI', 18, 'bold'), foreground="#2c3e50", background="#ecf0f1")

    def conf_gui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill='both')

        # Título
        ttk.Label(main_frame, text="🧵 Textiles Rosy", style="Title.TLabel").pack(pady=30)

        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(expand=True, pady=10)

        ancho_btn = 30  # ancho estándar

        ttk.Button(btn_frame, text="📦 Módulo de Inventario", command=self.abrir_inventario, width=ancho_btn).pack(pady=6)
        ttk.Button(btn_frame, text="💰 Módulo de Ventas", command=self.abrir_ventas, width=ancho_btn).pack(pady=6)
        ttk.Button(btn_frame, text="👥 Módulo de RRHH", command=self.abrir_rrhh, width=ancho_btn).pack(pady=6)
        ttk.Button(btn_frame, text="📊 Módulo de Finanzas", command=self.abrir_finanzas, width=ancho_btn).pack(pady=6)

        # Separador y botón de salida
        ttk.Separator(main_frame).pack(fill='x', pady=15)
        ttk.Button(main_frame, text="🚪 Salir del Sistema", command=self.cerrar_aplicacion, style="Accent.TButton").pack(pady=10)

    def abrir_inventario(self):
        if self.modulo_inventario is None or not self.modulo_inventario.window.winfo_exists():
            self.modulo_inventario = InventarioTextiles(self.root)
            if self.modulo_ventas:
                self.modulo_ventas.inventario = self.modulo_inventario
            if self.modulo_finanzas:
                self.modulo_finanzas.modulo_inventario = self.modulo_inventario

    def abrir_ventas(self):
        if self.modulo_ventas is None or not self.modulo_ventas.window.winfo_exists():
            inventario_ref = self.modulo_inventario if self.modulo_inventario else None
            self.modulo_ventas = VentasTextiles(self.root, inventario_ref)
            if self.modulo_finanzas:
                self.modulo_finanzas.modulo_ventas = self.modulo_ventas

    def abrir_rrhh(self):
        if self.modulo_rrhh is None or not self.modulo_rrhh.window.winfo_exists():
            self.modulo_rrhh = RecursosHumanos(self.root)
            if self.modulo_finanzas:
                self.modulo_finanzas.modulo_rrhh = self.modulo_rrhh

    def abrir_finanzas(self):
        if self.modulo_finanzas is None or not self.modulo_finanzas.window.winfo_exists():
            self.modulo_finanzas = FinanzasTextiles(
                self.root,
                ventas=self.modulo_ventas,
                inventario=self.modulo_inventario,
                rrhh=self.modulo_rrhh
            )

    def cerrar_aplicacion(self):
        modulos = [self.modulo_finanzas, self.modulo_rrhh, self.modulo_ventas, self.modulo_inventario]
        for modulo in modulos:
            if modulo and hasattr(modulo, 'window'):
                try:
                    modulo.window.destroy()
                except:
                    pass
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TextilesRosy()
    app.run()
