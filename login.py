import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from inventario_textiles import InventarioTextiles
from ventas_textiles import VentasTextiles
from recursos_humanos import RecursosHumanos
from finanzas_textiles import FinanzasTextiles

class SistemaAutenticacion:
    USUARIOS_FILE = "usuarios.json"
    
    def __init__(self):
        self.usuarios = {}
        self.cargar_usuarios()
        self.crear_admin_si_no_existe()
    
    def cargar_usuarios(self):
        if os.path.exists(self.USUARIOS_FILE):
            with open(self.USUARIOS_FILE, 'r') as f:
                self.usuarios = json.load(f)
    
    def guardar_usuarios(self):
        with open(self.USUARIOS_FILE, 'w') as f:
            json.dump(self.usuarios, f, indent=4)
    
    def crear_admin_si_no_existe(self):
        if "admin" not in self.usuarios:
            self.usuarios["admin"] = {
                "password": "admin123",
                "modulos": ["inventario", "ventas", "rrhh", "finanzas"],
                "es_admin": True
            }
            self.guardar_usuarios()
    
    def autenticar(self, usuario, password):
        if usuario in self.usuarios and self.usuarios[usuario]["password"] == password:
            return True
        return False
    
    def crear_usuario(self, usuario, password, modulos, admin=False):
        if usuario in self.usuarios:
            return False, "El usuario ya existe"
        
        self.usuarios[usuario] = {
            "password": password,
            "modulos": modulos,
            "es_admin": admin
        }
        self.guardar_usuarios()
        return True, "Usuario creado exitosamente"
    
    def obtener_modulos_usuario(self, usuario):
        if usuario in self.usuarios:
            return self.usuarios[usuario]["modulos"]
        return []
    
    def es_admin(self, usuario):
        if usuario in self.usuarios:
            return self.usuarios[usuario].get("es_admin", False)
        return False

class LoginWindow:
    def __init__(self, root, sistema_auth, on_login_success):
        self.root = root
        self.sistema_auth = sistema_auth
        self.on_login_success = on_login_success
        
        self.window = tk.Toplevel(root)
        self.window.title("Iniciar Sesión - Textiles Rosy")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.grab_set()
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Inicio de Sesión", style="Title.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=20)
        
        # Usuario
        ttk.Label(form_frame, text="Usuario:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.usuario_entry = ttk.Entry(form_frame)
        self.usuario_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Contraseña
        ttk.Label(form_frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Iniciar Sesión", command=self.intentar_login).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.window.destroy).pack(side="right", padx=5)
    
    def intentar_login(self):
        usuario = self.usuario_entry.get()
        password = self.password_entry.get()
        
        if not usuario or not password:
            messagebox.showerror("Error", "Usuario y contraseña son requeridos")
            return
        
        if self.sistema_auth.autenticar(usuario, password):
            self.window.destroy()
            self.on_login_success(usuario)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

class CrearUsuarioWindow:
    def __init__(self, root, sistema_auth):
        self.root = root
        self.sistema_auth = sistema_auth
        
        self.window = tk.Toplevel(root)
        self.window.title("Crear Nuevo Usuario - Textiles Rosy")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.grab_set()
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Crear Nuevo Usuario", style="Title.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)
        
        # Usuario
        ttk.Label(form_frame, text="Nuevo Usuario:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.usuario_entry = ttk.Entry(form_frame)
        self.usuario_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Contraseña
        ttk.Label(form_frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Confirmar Contraseña
        ttk.Label(form_frame, text="Confirmar Contraseña:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.confirm_password_entry = ttk.Entry(form_frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Módulos
        ttk.Label(form_frame, text="Módulos Permitidos:").grid(row=3, column=0, padx=5, pady=5, sticky="ne")
        
        modulos_frame = ttk.Frame(form_frame)
        modulos_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        self.modulos_vars = {
            "inventario": tk.BooleanVar(),
            "ventas": tk.BooleanVar(),
            "rrhh": tk.BooleanVar(),
            "finanzas": tk.BooleanVar()
        }
        
        ttk.Checkbutton(modulos_frame, text="Inventario", variable=self.modulos_vars["inventario"]).pack(anchor="w")
        ttk.Checkbutton(modulos_frame, text="Ventas", variable=self.modulos_vars["ventas"]).pack(anchor="w")
        ttk.Checkbutton(modulos_frame, text="RRHH", variable=self.modulos_vars["rrhh"]).pack(anchor="w")
        ttk.Checkbutton(modulos_frame, text="Finanzas", variable=self.modulos_vars["finanzas"]).pack(anchor="w")
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Crear Usuario", command=self.crear_usuario).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.window.destroy).pack(side="right", padx=5)
    
    def crear_usuario(self):
        usuario = self.usuario_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not usuario or not password or not confirm_password:
            messagebox.showerror("Error", "Todos los campos son requeridos")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        modulos_seleccionados = [modulo for modulo, var in self.modulos_vars.items() if var.get()]
        
        if not modulos_seleccionados:
            messagebox.showerror("Error", "Debe seleccionar al menos un módulo")
            return
        
        success, mensaje = self.sistema_auth.crear_usuario(usuario, password, modulos_seleccionados)
        
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.window.destroy()
        else:
            messagebox.showerror("Error", mensaje)

class TextilesRosy:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Integral - Textiles Rosy")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        self.root.configure(bg="#ecf0f1")
        self.root.resizable(True, True)
        
        self.sistema_auth = SistemaAutenticacion()
        self.usuario_actual = None
        
        self.modulo_inventario = None
        self.modulo_ventas = None
        self.modulo_rrhh = None
        self.modulo_finanzas = None

        self.conf_estilo()
        self.mostrar_login()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def conf_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(".", background="#ecf0f1", foreground="#2c3e50", font=('Segoe UI', 10))
        style.configure("TButton", background="#2980b9", foreground="white", padding=10, font=('Segoe UI', 10, 'bold'))
        style.map("TButton", background=[('active', '#3498db')])
        style.configure("Accent.TButton", background="#c0392b", foreground="white")
        style.map("Accent.TButton", background=[('active', '#e74c3c')])
        style.configure("Title.TLabel", font=('Segoe UI', 18, 'bold'), foreground="#2c3e50", background="#ecf0f1")

    def mostrar_login(self):
        LoginWindow(self.root, self.sistema_auth, self.on_login_success)

    def on_login_success(self, usuario):
        self.usuario_actual = usuario
        self.conf_gui()
        self.actualizar_interfaz_segun_permisos()

    def conf_gui(self):
        # Limpiar ventana principal si ya tenía contenido
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill='both')

        # Barra superior con información de usuario
        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill='x', pady=(0, 20))
        
        ttk.Label(top_bar, text=f"Usuario: {self.usuario_actual}", font=('Segoe UI', 10)).pack(side='left')
        
        if self.sistema_auth.es_admin(self.usuario_actual):
            ttk.Button(top_bar, text="➕ Crear Usuario", command=self.mostrar_crear_usuario, 
                      style="TButton", padding=5).pack(side='right', padx=5)
        
        ttk.Button(top_bar, text="🔒 Cerrar Sesión", command=self.cerrar_sesion, 
                  style="Accent.TButton", padding=5).pack(side='right')

        # Título
        ttk.Label(main_frame, text="🧵 Textiles Rosy", style="Title.TLabel").pack(pady=30)

        # Botones de módulos (se actualizarán según permisos)
        self.btn_frame = ttk.Frame(main_frame)
        self.btn_frame.pack(expand=True, pady=10)
        
        # Separador y botón de salida
        ttk.Separator(main_frame).pack(fill='x', pady=15)
        ttk.Button(main_frame, text="🚪 Salir del Sistema", command=self.cerrar_aplicacion, 
                  style="Accent.TButton").pack(pady=10)

    def actualizar_interfaz_segun_permisos(self):
        # Limpiar botones existentes
        for widget in self.btn_frame.winfo_children():
            widget.destroy()
        
        modulos_permitidos = self.sistema_auth.obtener_modulos_usuario(self.usuario_actual)
        es_admin = self.sistema_auth.es_admin(self.usuario_actual)
        
        ancho_btn = 30
        
        if "inventario" in modulos_permitidos or es_admin:
            ttk.Button(self.btn_frame, text="📦 Módulo de Inventario", command=self.abrir_inventario, 
                      width=ancho_btn).pack(pady=6)
        
        if "ventas" in modulos_permitidos or es_admin:
            ttk.Button(self.btn_frame, text="💰 Módulo de Ventas", command=self.abrir_ventas, 
                      width=ancho_btn).pack(pady=6)
        
        if "rrhh" in modulos_permitidos or es_admin:
            ttk.Button(self.btn_frame, text="👥 Módulo de RRHH", command=self.abrir_rrhh, 
                      width=ancho_btn).pack(pady=6)
        
        if "finanzas" in modulos_permitidos or es_admin:
            ttk.Button(self.btn_frame, text="📊 Módulo de Finanzas", command=self.abrir_finanzas, 
                      width=ancho_btn).pack(pady=6)

    def mostrar_crear_usuario(self):
        if self.sistema_auth.es_admin(self.usuario_actual):
            CrearUsuarioWindow(self.root, self.sistema_auth)
        else:
            messagebox.showerror("Error", "Solo el administrador puede crear usuarios")

    def cerrar_sesion(self):
        self.usuario_actual = None
        # Cerrar todos los módulos abiertos
        self.cerrar_modulos()
        # Mostrar ventana de login nuevamente
        self.mostrar_login()

    def cerrar_modulos(self):
        modulos = [self.modulo_finanzas, self.modulo_rrhh, self.modulo_ventas, self.modulo_inventario]
        for modulo in modulos:
            if modulo and hasattr(modulo, 'window'):
                try:
                    modulo.window.destroy()
                except:
                    pass
        self.modulo_inventario = None
        self.modulo_ventas = None
        self.modulo_rrhh = None
        self.modulo_finanzas = None

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
        self.cerrar_modulos()
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TextilesRosy()
    app.run()