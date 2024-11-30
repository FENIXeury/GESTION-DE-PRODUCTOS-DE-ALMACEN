import tkinter as tk
import pymysql
import uuid
from datetime import datetime
from tkinter import ttk, messagebox, PhotoImage
import os

# ------------------------------
# Clase para gestionar la conexión con la base de datos
# ------------------------------

class ConexionBD:
    def __init__(self, host, usuario, contrasena, base_datos):
        self.host = host
        self.usuario = usuario
        self.contrasena = contrasena
        self.base_datos = base_datos
        self.conn = None
        self.cursor = None

    def conectar(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.usuario,
                password=self.contrasena,
                database=self.base_datos,
                charset='utf8mb4'
            )
            self.cursor = self.conn.cursor()
            print("Conexión exitosa a la base de datos.")
        except pymysql.MySQLError as e:
            print(f"Error al conectar con la base de datos: {e}")
    
    def cerrar(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
    
    def ejecutar_consulta(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except pymysql.MySQLError as e:
            print(f"Error al ejecutar consulta: {e}")
            self.conn.rollback()
    
    def obtener_resultados(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"Error al obtener resultados: {e}")
            return []


# ------------------------------
# Variable global para el usuario logueado
# ------------------------------
usuario_logueado = None  # Variable global para almacenar el nombre del usuario logueado

# ------------------------------
# Clase Usuario (Encapsulamiento)
# ------------------------------

class Usuario:
    def __init__(self, usuarios, correo, contrasena, rol, estado, token=None):
        self.__usuarios = usuarios
        self.__correo = correo
        self.__contrasena = contrasena
        self.__rol = rol
        self.__estado = estado
        self.__token = token
        self.__fecha_creacion = datetime.now()

    # Métodos getter y setter para el acceso controlado
    @property
    def usuarios(self):
        return self.__usuarios

    @property
    def correo(self):
        return self.__correo

    @property
    def contrasena(self):
        return self.__contrasena

    @property
    def rol(self):
        return self.__rol

    @property
    def estado(self):
        return self.__estado

    @property
    def token(self):
        return self.__token

    @property
    def fecha_creacion(self):
        return self.__fecha_creacion

    # Método para verificar el login
    def verificar_login(self, conexion: ConexionBD):
        conexion.conectar()
        # Realizamos la consulta para buscar el nombre de usuario y contraseña
        conexion.cursor.execute(
            "SELECT nombre_usuario FROM usuarios WHERE usuarios=%s AND contrasena=%s", 
            (self.__usuarios, self.__contrasena)
        )
        usuario = conexion.cursor.fetchone()
        conexion.cerrar()

        # Si se encuentra un usuario, asignamos el nombre de usuario a la variable global
        if usuario:
            global usuario_logueado
            usuario_logueado = usuario[0]  # Asignamos nombre_usuario
            return True  # Login exitoso
        else:
            usuario_logueado = None
            return False  # Login fallido

    # Método para registrar un nuevo usuario
    def registrar_usuario(self, conexion: ConexionBD):
        conexion.conectar()
        try:
            # Generar token único
            self.__token = str(uuid.uuid4()) #token para identificar usuarios de manera unica
            fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conexion.cursor.execute(""" 
                INSERT INTO usuarios (usuarios, contrasena, rol, estado, token, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.__usuarios, self.__contrasena, self.__rol, self.__estado, self.__token, fecha_creacion))
            conexion.conn.commit()
            print("Usuario registrado con éxito.")
        except pymysql.MySQLError as err:
            print(f"Error al registrar usuario: {err}")
            messagebox.showerror("Error", f"No se pudo registrar el usuario: {err}")
        finally:
            conexion.cerrar()


# ------------------------------
# Clase Base para la Ventana
# ------------------------------

class VentanaBase:
    def __init__(self, root):
        self.root = root

    def cerrar(self):
        self.root.quit()

# ------------------------------
# Clase VentanaLogin
# ------------------------------

class VentanaLogin(VentanaBase):
    def __init__(self, root, conexion_bd):
        super().__init__(root)
        self.conexion_bd = conexion_bd
        self.root.title("Login")
        self.root.geometry("400x500")
        self.root.config(bg="#f0f0f0")  # Fondo claro

        # Título de la ventana
        label_titulo = tk.Label(self.root, text="Iniciar Sesión", font=("Helvetica", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        label_titulo.pack(pady=20)

        # Campo de nombre de usuario
        self.label_usuarios = tk.Label(self.root, text="Nombre de usuario:", font=("Helvetica", 12), bg="#f0f0f0", fg="#34495e")
        self.label_usuarios.pack(pady=5)

        self.entry_usuarios = tk.Entry(self.root, font=("Helvetica", 12), bg="#ecf0f1", fg="#34495e", bd=2, relief="solid", width=30)
        self.entry_usuarios.pack(pady=10)
        self.entry_usuarios.focus()  # Foco en el campo de usuario

        # Campo de contraseña
        self.label_contrasena = tk.Label(self.root, text="Contraseña:", font=("Helvetica", 12), bg="#f0f0f0", fg="#34495e")
        self.label_contrasena.pack(pady=5)

        self.entry_contrasena = tk.Entry(self.root, font=("Helvetica", 12), bg="#ecf0f1", fg="#34495e", bd=2, relief="solid", show="*", width=30)
        self.entry_contrasena.pack(pady=10)

        # Botón de Iniciar sesión
        self.boton_login = tk.Button(self.root, text="Iniciar sesión", command=self.login, bg="#3498db", fg="white", font=("Helvetica", 14), relief="flat", width=20)
        self.boton_login.pack(pady=20)

        # Botón de Registrarse
        self.boton_registrarse = tk.Button(self.root, text="Registrarse", command=self.registrarse, bg="#95a5a6", fg="white", font=("Helvetica", 10), relief="flat", width=20)
        self.boton_registrarse.pack(pady=5)

        # Efectos de hover para los botones
        self.boton_login.bind("<Enter>", lambda e: self.hover_boton(self.boton_login, True))
        self.boton_login.bind("<Leave>", lambda e: self.hover_boton(self.boton_login, False))
        self.boton_registrarse.bind("<Enter>", lambda e: self.hover_boton(self.boton_registrarse, True))
        self.boton_registrarse.bind("<Leave>", lambda e: self.hover_boton(self.boton_registrarse, False))

    def hover_boton(self, boton, hover):
        """Efecto de hover para botones"""
        if hover:
            boton.config(bg="#2980b9")  # Color más oscuro al pasar el ratón
        else:
            boton.config(bg="#3498db")  # Color original

    def login(self):
        """Verificar credenciales de usuario"""
        usuarios = self.entry_usuarios.get()
        contrasena = self.entry_contrasena.get()

        usuario = Usuario(usuarios, "", contrasena, "", "", "")
        if usuario.verificar_login(self.conexion_bd):
            print("Login exitoso")
            messagebox.showinfo("Login exitoso", "Bienvenido!")
            self.root.withdraw()  # Ocultar la ventana de login
            dashboard = Dashboard(self.root, self.conexion_bd)
            dashboard.mostrar_dashboard()  # Mostrar el Dashboard
        else:
            messagebox.showerror("Error", "Nombre de usuario o contraseña incorrectos.")

    def registrarse(self):
        """Abrir la ventana de registro"""
        ventana_registro = tk.Toplevel(self.root)
        VentanaRegistro(ventana_registro, self.conexion_bd)
# ------------------------------
# Clase Dashboard
# ------------------------------

class Dashboard:
    def __init__(self, root, conexion_bd):
        self.root = root
        self.conexion_bd = conexion_bd
        self.ventana_dashboard = None
        self.frame_contenido = None
        self.usuario_logueado = "admin"
    def mostrar_dashboard(self):
        # Definir las rutas de las imágenes
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icono_usuarios_path = os.path.join(script_dir, "recursos/1.png")
        icono_productos_path = os.path.join(script_dir, "recursos/2.png")
        fondo_path = os.path.join(script_dir, "recursos/fondo.png")

        # Crear la ventana del Dashboard
        self.ventana_dashboard = tk.Toplevel(self.root)
        self.ventana_dashboard.title("Dashboard - Sistema de Gestión")
        self.ventana_dashboard.geometry("800x600")

        # Interceptar el evento de cierre de la ventana
        self.ventana_dashboard.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Encabezado de la ventana
        encabezado = tk.Frame(self.ventana_dashboard, bg="#34495E", height=50)
        encabezado.pack(side="top", fill="x")

        label_titulo = tk.Label(encabezado, text="Sistema de Gestión de Productos", font=("Arial", 14), fg="#808080")
        label_titulo.pack(side="left", padx=20)

        label_usuario = tk.Label(encabezado, text=f"Usuario: {self.usuario_logueado}", font=("Arial", 12), fg="#808080")
        label_usuario.pack(side="right", padx=20)

        # Menú izquierdo
        menu_izquierdo = tk.Frame(self.ventana_dashboard, width=200, height=600, bg="#2C3E50")
        menu_izquierdo.pack(side="left", fill="y", anchor="n")

        # Cargar iconos
        icono_usuarios = PhotoImage(file=icono_usuarios_path)
        icono_productos = PhotoImage(file=icono_productos_path)

        # Botones del menú izquierdo
        boton_dashboard = tk.Button(menu_izquierdo, text="Dashboard", bg="#34495E", fg="white", font=("Arial", 12), command=self.mostrar_dashboard)
        boton_dashboard.pack(pady=10)

        boton_usuarios = tk.Button(menu_izquierdo, text="Gestión de Usuarios", bg="#34495E", fg="white", font=("Arial", 12), image=icono_usuarios, compound="left", command=self.gestion_usuarios)
        boton_usuarios.image = icono_usuarios  # Para evitar que se borre el icono
        boton_usuarios.pack(pady=10)

        boton_productos = tk.Button(menu_izquierdo, text="Gestión de Productos", bg="#34495E", fg="white", font=("Arial", 12), image=icono_productos, compound="left", command=self.gestion_productos)
        boton_productos.image = icono_productos  # Para evitar que se borre el icono
        boton_productos.pack(pady=10)

        # Botón "Cerrar sesión" en la parte inferior del menú izquierdo
        boton_salir = tk.Button(menu_izquierdo, text="Cerrar sesión", bg="#E74C3C", fg="white", font=("Arial", 12), command=self.cerrar_sesion)
        boton_salir.pack(side="bottom", pady=20)

        # Área de contenido vacía con imagen de fondo
        self.frame_contenido = tk.Frame(self.ventana_dashboard, bg="#ecf0f1")
        self.frame_contenido.pack(side="right", fill="both", expand=True)

        # Cargar imagen de fondo
        fondo_imagen = PhotoImage(file=fondo_path)

        # Crear un label con la imagen de fondo, que respeta sus dimensiones originales
        label_fondo = tk.Label(self.frame_contenido, image=fondo_imagen)
        label_fondo.place(relwidth=1, relheight=1)  # La imagen ocupa toda el área disponible

        # Es importante mantener una referencia a la imagen para evitar que se elimine
        label_fondo.image = fondo_imagen

    def on_closing(self):
        """Este método se ejecuta al intentar cerrar la ventana del Dashboard."""
        respuesta = messagebox.askyesno("Cerrar ventana", "¿Estás seguro de que quieres salir, no es mejor darle a cerrar sesion (:?")
        if respuesta:
            self.ventana_dashboard.destroy()  # Cierra la ventana
            self.root.quit()  # Termina la ejecución del programa
            print("Sesión cerrada y aplicación cerrada")
        else:
            print("Cierre de sesión cancelado")
            return  # Si no se confirma, la ventana permanece abierta

    def cerrar_sesion(self):
        """Cierra la sesión y termina la ejecución del programa."""
        respuesta = messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que quieres cerrar la sesión?")
        if respuesta:
            self.ventana_dashboard.destroy()  # Destruir la ventana del dashboard
            self.root.quit()  # Termina la ejecución de la aplicación
            print("Sesión cerrada y aplicación cerrada")
        else:
            print("Cierre de sesión cancelado")
    #GESTION USUARIOS
    def gestion_usuarios(self):
        """Función que abre la ventana de gestión de usuarios y muestra un listado con sus detalles"""
        print("Abriendo gestión de usuarios...")

        # Crear la nueva ventana para gestionar usuarios
        ventana_usuarios = tk.Toplevel(self.ventana_dashboard)
        ventana_usuarios.title("Gestión de Usuarios")
        ventana_usuarios.geometry("800x600")

        # Crear el encabezado de la ventana de gestión
        label_titulo = tk.Label(ventana_usuarios, text="Listado de Usuarios Registrados", font=("Arial", 14))
        label_titulo.pack(pady=10)

        # Crear el árbol de visualización de usuarios (usando Treeview de tkinter)
        columnas = ("ID Cliente", "Nombre", "Apellido", "Número de Teléfono", "Correo Electrónico", "Usuario")

        treeview = ttk.Treeview(ventana_usuarios, columns=columnas, show="headings", height=15)
        treeview.pack(pady=10, padx=20, fill="both", expand=True)

        # Configurar las columnas
        treeview.heading("ID Cliente", text="ID Cliente")
        treeview.heading("Nombre", text="Nombre")
        treeview.heading("Apellido", text="Apellido")
        treeview.heading("Número de Teléfono", text="Número de Teléfono")
        treeview.heading("Correo Electrónico", text="Correo Electrónico")
        treeview.heading("Usuario", text="Usuario")

        # Configurar el ancho de las columnas
        treeview.column("ID Cliente", width=80, anchor="w")
        treeview.column("Nombre", width=150, anchor="w")
        treeview.column("Apellido", width=150, anchor="w")
        treeview.column("Número de Teléfono", width=150, anchor="w")
        treeview.column("Correo Electrónico", width=200, anchor="w")
        treeview.column("Usuario", width=150, anchor="w")

        # Conectar a la base de datos para obtener la lista de usuarios
        self.conexion_bd.conectar()

        try:
            # Consulta SQL para obtener los datos de la tabla clientes
            query = """
            SELECT id_cliente, nombre, apellido, telefono, correo_electronico, usuario FROM clientes
            """
            self.conexion_bd.cursor.execute(query)
            usuarios = self.conexion_bd.cursor.fetchall()

            # Agregar los usuarios al treeview
            for usuario in usuarios:
                treeview.insert("", "end", values=usuario)

        except pymysql.MySQLError as e:
            print(f"Error al obtener usuarios: {e}")
            messagebox.showerror("Error", "No se pudieron obtener los datos de los usuarios.")

        finally:
            self.conexion_bd.cerrar()

        # Función para cambiar el color de fondo de una fila seleccionada
        # Función para cambiar el color de fondo de una fila seleccionada y mostrar un alert
        def seleccionar_fila(event):
            item = treeview.focus()  # Obtener la fila seleccionada
            if item:
                # Cambiar el color de fondo a verde
                treeview.item(item, tags="seleccionada")

                # Obtener los datos del usuario seleccionado
                usuario_seleccionado = treeview.item(item)['values']

                # Mostrar un alert con el mensaje de éxito
                messagebox.showinfo("Éxito", f"Usuario seleccionado: {usuario_seleccionado[1]} {usuario_seleccionado[2]}", icon='info')

                # Crear un mensaje visual dentro de la ventana (por ejemplo, debajo del treeview)
                label_mensaje.config(text=f"Usuario seleccionado: {usuario_seleccionado[1]} {usuario_seleccionado[2]}", fg="green")

        # Añadir estilo para filas seleccionadas
        treeview.tag_configure("seleccionada", background="lightgreen")

        # Asociar la función de cambio de color con el evento de clic en las filas
        treeview.bind("<ButtonRelease-1>", seleccionar_fila)

        # Crear un label para mostrar el mensaje de éxito (lo pondremos debajo del treeview)
        label_mensaje = tk.Label(ventana_usuarios, text="", font=("Arial", 12), fg="green")
        label_mensaje.pack(pady=10)

        # Botones de gestión
        frame_botones = tk.Frame(ventana_usuarios)
        frame_botones.pack(pady=20)

        # Botón de nuevo cliente
        boton_nuevo = tk.Button(frame_botones, text="Nuevo", bg="#2ECC71", fg="white", font=("Arial", 12),
                                command=lambda: self.abrir_ventana_nuevo_cliente(treeview))  # Pasamos treeview aquí
        boton_nuevo.grid(row=0, column=0, padx=10)

        # Botón de editar
        boton_editar = tk.Button(frame_botones, text="Editar", bg="#F39C12", fg="white", font=("Arial", 12),
                                 command=lambda: self.editar_usuario(treeview))  # Llamamos la función de editar
        boton_editar.grid(row=0, column=4, padx=10)

        # Botón de actualizar
        boton_actualizar = tk.Button(frame_botones, text="Actualizar", bg="#3498DB", fg="white", font=("Arial", 12),
                                     command=lambda: self.actualizar_usuarios(treeview))
        boton_actualizar.grid(row=0, column=1, padx=10)

        # Botón de eliminar
        boton_eliminar = tk.Button(frame_botones, text="Eliminar", bg="#E74C3C", fg="white", font=("Arial", 12), command=lambda: self.eliminar_usuario(treeview))
        boton_eliminar.grid(row=0, column=2, padx=10)

        # Botón de salir
        boton_salir = tk.Button(frame_botones, text="Salir", bg="#95A5A6", fg="white", font=("Arial", 12), command=ventana_usuarios.destroy)
        boton_salir.grid(row=0, column=3, padx=10)
    def actualizar_usuarios(self, treeview):
        # Limpiar los datos actuales en el treeview
        for item in treeview.get_children():
            treeview.delete(item)

        # Volver a obtener los datos actualizados de la base de datos
        self.conexion_bd.conectar()

        try:
            # Consulta SQL para obtener los datos actualizados de la tabla clientes
            query = """
            SELECT id_cliente, nombre, apellido, telefono, correo_electronico, usuario FROM clientes
            """
            self.conexion_bd.cursor.execute(query)
            usuarios = self.conexion_bd.cursor.fetchall()

            # Agregar los usuarios al treeview
            for usuario in usuarios:
                treeview.insert("", "end", values=usuario)

        except pymysql.MySQLError as e:
            print(f"Error al obtener usuarios: {e}")
            messagebox.showerror("Error", "No se pudieron obtener los datos de los usuarios.")

        finally:
            self.conexion_bd.cerrar()
    def abrir_ventana_nuevo_cliente(self, treeview):
        """Función para abrir la ventana para agregar un nuevo cliente"""
        ventana_nuevo_cliente = tk.Toplevel(self.ventana_dashboard)
        ventana_nuevo_cliente.title("Nuevo Cliente")
        ventana_nuevo_cliente.geometry("400x500")

        label_nombre = tk.Label(ventana_nuevo_cliente, text="Nombre:")
        label_nombre.pack(pady=10)
        entry_nombre = tk.Entry(ventana_nuevo_cliente)
        entry_nombre.pack(pady=10)

        label_apellido = tk.Label(ventana_nuevo_cliente, text="Apellido:")
        label_apellido.pack(pady=10)
        entry_apellido = tk.Entry(ventana_nuevo_cliente)
        entry_apellido.pack(pady=10)

        label_telefono = tk.Label(ventana_nuevo_cliente, text="Teléfono:")
        label_telefono.pack(pady=10)
        entry_telefono = tk.Entry(ventana_nuevo_cliente)
        entry_telefono.pack(pady=10)

        label_correo = tk.Label(ventana_nuevo_cliente, text="Correo Electrónico:")
        label_correo.pack(pady=10)
        entry_correo = tk.Entry(ventana_nuevo_cliente)
        entry_correo.pack(pady=10)

        label_usuario = tk.Label(ventana_nuevo_cliente, text="Usuario:")
        label_usuario.pack(pady=10)
        entry_usuario = tk.Entry(ventana_nuevo_cliente)
        entry_usuario.pack(pady=10)

        def guardar_nuevo_cliente():
            nombre = entry_nombre.get()
            apellido = entry_apellido.get()
            telefono = entry_telefono.get()
            correo = entry_correo.get()
            usuario = entry_usuario.get()

            if nombre and apellido and telefono and correo and usuario:
                try:
                    self.conexion_bd.conectar()
                    query_insertar = """
                    INSERT INTO clientes (nombre, apellido, telefono, correo_electronico, usuario)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    self.conexion_bd.cursor.execute(query_insertar, (nombre, apellido, telefono, correo, usuario))
                    self.conexion_bd.conn.commit()
                    messagebox.showinfo("Éxito", "Nuevo cliente agregado.")
                    ventana_nuevo_cliente.destroy()

                    # Aquí se llama a la función para actualizar el treeview de la ventana principal
                    self.actualizar_usuarios(treeview)  # Recargar la lista de usuarios
                except pymysql.MySQLError as e:
                    print(f"Error al agregar el cliente: {e}")
                    messagebox.showerror("Error", "Hubo un problema al agregar el cliente.")

        boton_guardar = tk.Button(ventana_nuevo_cliente, text="Guardar", command=guardar_nuevo_cliente)
        boton_guardar.pack(pady=20)
    def eliminar_usuario(self, treeview):
        selected_items = treeview.selection()
        if not selected_items:
            messagebox.showerror("Error", "Por favor seleccione un usuario para eliminar.")
            return

        selected_item = selected_items[0]
        id_cliente = treeview.item(selected_item)['values'][0]

        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este usuario?")
        if respuesta:
            self.conexion_bd.conectar()
            try:
                query = "DELETE FROM clientes WHERE id_cliente = %s"
                self.conexion_bd.cursor.execute(query, (id_cliente,))
                self.conexion_bd.conn.commit()
                messagebox.showinfo("Éxito", "Usuario eliminado exitosamente.")
                self.actualizar_usuarios(treeview)  # Recargar la lista de usuarios
            except pymysql.MySQLError as e:
                print(f"Error al eliminar el usuario: {e}")
                messagebox.showerror("Error", "Hubo un problema al eliminar el usuario.")
    def editar_usuario(self, treeview):

        selected_items = treeview.selection()
        if not selected_items:
            messagebox.showerror("Error", "Por favor seleccione un usuario para editar.")
            return

        selected_item = selected_items[0]
        id_cliente = treeview.item(selected_item)['values'][0]
        nombre = treeview.item(selected_item)['values'][1]
        apellido = treeview.item(selected_item)['values'][2]
        telefono = treeview.item(selected_item)['values'][3]
        correo = treeview.item(selected_item)['values'][4]
        usuario = treeview.item(selected_item)['values'][5]

        # Crear la ventana de edición
        ventana_editar = tk.Toplevel(self.ventana_dashboard)
        ventana_editar.title("Editar Usuario")
        ventana_editar.geometry("400x500")

        # Entradas de texto pre-llenadas con los valores actuales
        label_nombre = tk.Label(ventana_editar, text="Nombre:")
        label_nombre.pack(pady=10)
        entry_nombre = tk.Entry(ventana_editar)
        entry_nombre.insert(0, nombre)  # Rellenar con el valor actual
        entry_nombre.pack(pady=10)

        label_apellido = tk.Label(ventana_editar, text="Apellido:")
        label_apellido.pack(pady=10)
        entry_apellido = tk.Entry(ventana_editar)
        entry_apellido.insert(0, apellido)  # Rellenar con el valor actual
        entry_apellido.pack(pady=10)

        label_telefono = tk.Label(ventana_editar, text="Teléfono:")
        label_telefono.pack(pady=10)
        entry_telefono = tk.Entry(ventana_editar)
        entry_telefono.insert(0, telefono)  # Rellenar con el valor actual
        entry_telefono.pack(pady=10)

        label_correo = tk.Label(ventana_editar, text="Correo Electrónico:")
        label_correo.pack(pady=10)
        entry_correo = tk.Entry(ventana_editar)
        entry_correo.insert(0, correo)  # Rellenar con el valor actual
        entry_correo.pack(pady=10)

        label_usuario = tk.Label(ventana_editar, text="Usuario:")
        label_usuario.pack(pady=10)
        entry_usuario = tk.Entry(ventana_editar)
        entry_usuario.insert(0, usuario)  # Rellenar con el valor actual
        entry_usuario.pack(pady=10)

        def guardar_edicion():
            # Obtener los nuevos valores
            nuevo_nombre = entry_nombre.get()
            nuevo_apellido = entry_apellido.get()
            nuevo_telefono = entry_telefono.get()
            nuevo_correo = entry_correo.get()
            nuevo_usuario = entry_usuario.get()

            # Actualizar en la base de datos
            if nuevo_nombre and nuevo_apellido and nuevo_telefono and nuevo_correo and nuevo_usuario:
                try:
                    self.conexion_bd.conectar()
                    query_actualizar = """
                    UPDATE clientes
                    SET nombre = %s, apellido = %s, telefono = %s, correo_electronico = %s, usuario = %s
                    WHERE id_cliente = %s
                    """
                    self.conexion_bd.cursor.execute(query_actualizar, (nuevo_nombre, nuevo_apellido, nuevo_telefono, nuevo_correo, nuevo_usuario, id_cliente))
                    self.conexion_bd.conn.commit()
                    messagebox.showinfo("Éxito", "Datos del cliente actualizados.")
                    ventana_editar.destroy()
                    self.actualizar_usuarios(treeview)  # Recargar los datos en el Treeview
                except pymysql.MySQLError as e:
                    print(f"Error al actualizar el cliente: {e}")
                    messagebox.showerror("Error", "Hubo un problema al actualizar los datos.")

            # Botón para guardar la edición
            boton_guardar = tk.Button(ventana_editar, text="Guardar", command=guardar_edicion)
            boton_guardar.pack(pady=20)
    #GESTION2 PRODUCTOS
    def gestion_productos(self):
        """Función que abre la ventana de gestión de productos y muestra un listado con sus detalles"""
        print("Abriendo gestión de productos...")

        # Crear la nueva ventana para gestionar productos
        ventana_productos = tk.Toplevel(self.ventana_dashboard)
        ventana_productos.title("Gestión de Productos")
        ventana_productos.geometry("800x600")

        # Crear el encabezado de la ventana de gestión
        label_titulo = tk.Label(ventana_productos, text="Listado de Productos Registrados", font=("Arial", 14))
        label_titulo.pack(pady=10)

        # Crear el árbol de visualización de productos (usando Treeview de tkinter)
        columnas = ("ID Producto", "Nombre", "Categoría", "Precio", "Cantidad", "Descripción")

        treeview = ttk.Treeview(ventana_productos, columns=columnas, show="headings", height=15)
        treeview.pack(pady=10, padx=20, fill="both", expand=True)

        # Configurar las columnas
        treeview.heading("ID Producto", text="ID Producto")
        treeview.heading("Nombre", text="Nombre")
        treeview.heading("Categoría", text="Categoría")
        treeview.heading("Precio", text="Precio")
        treeview.heading("Cantidad", text="Cantidad")
        treeview.heading("Descripción", text="Descripción")

        # Configurar el ancho de las columnas
        treeview.column("ID Producto", width=80, anchor="w")
        treeview.column("Nombre", width=150, anchor="w")
        treeview.column("Categoría", width=150, anchor="w")
        treeview.column("Precio", width=100, anchor="w")
        treeview.column("Cantidad", width=100, anchor="w")
        treeview.column("Descripción", width=200, anchor="w")

        # Conectar a la base de datos para obtener la lista de productos
        self.conexion_bd.conectar()

        try:
            # Consulta SQL para obtener los datos de la tabla productos
            query = """
            SELECT id_producto, nombre, categoria, precio, cantidad, descripcion FROM productos
            """
            self.conexion_bd.cursor.execute(query)
            productos = self.conexion_bd.cursor.fetchall()

            # Agregar los productos al treeview
            for producto in productos:
                treeview.insert("", "end", values=producto)

        except pymysql.MySQLError as e:
            print(f"Error al obtener productos: {e}")
            messagebox.showerror("Error", "No se pudieron obtener los datos de los productos.")

        finally:
            self.conexion_bd.cerrar()

        # Función para cambiar el color de fondo de una fila seleccionada y mostrar un alert
        def seleccionar_fila(event):
            item = treeview.focus()  # Obtener la fila seleccionada
            if item:
                # Cambiar el color de fondo a verde
                treeview.item(item, tags="seleccionada")

                # Obtener los datos del producto seleccionado
                producto_seleccionado = treeview.item(item)['values']

                # Mostrar un alert con el mensaje de éxito
                messagebox.showinfo("Éxito", f"Producto seleccionado: {producto_seleccionado[1]}", icon='info')

                # Crear un mensaje visual dentro de la ventana (por ejemplo, debajo del treeview)
                label_mensaje.config(text=f"Producto seleccionado: {producto_seleccionado[1]}", fg="green")

        # Añadir estilo para filas seleccionadas
        treeview.tag_configure("seleccionada", background="lightgreen")

        # Asociar la función de cambio de color con el evento de clic en las filas
        treeview.bind("<ButtonRelease-1>", seleccionar_fila)

        # Crear un label para mostrar el mensaje de éxito (lo pondremos debajo del treeview)
        label_mensaje = tk.Label(ventana_productos, text="", font=("Arial", 12), fg="green")
        label_mensaje.pack(pady=10)

        # Botones de gestión
        frame_botones = tk.Frame(ventana_productos)
        frame_botones.pack(pady=20)

        # Botón de nuevo producto
        boton_nuevo = tk.Button(frame_botones, text="Nuevo", bg="#2ECC71", fg="white", font=("Arial", 12),
                                command=lambda: self.abrir_ventana_nuevo_producto(treeview))  # Pasamos treeview aquí
        boton_nuevo.grid(row=0, column=0, padx=10)

        # Botón de editar
        boton_editar = tk.Button(frame_botones, text="Editar", bg="#F39C12", fg="white", font=("Arial", 12),
                                 command=lambda: self.editar_producto(treeview))  # Llamamos la función de editar
        boton_editar.grid(row=0, column=4, padx=10)

        # Botón de actualizar
        boton_actualizar = tk.Button(frame_botones, text="Actualizar", bg="#3498DB", fg="white", font=("Arial", 12),
                                     command=lambda: self.actualizar_productos(treeview))
        boton_actualizar.grid(row=0, column=1, padx=10)

        # Botón de eliminar
        boton_eliminar = tk.Button(frame_botones, text="Eliminar", bg="#E74C3C", fg="white", font=("Arial", 12), command=lambda: self.eliminar_producto(treeview))
        boton_eliminar.grid(row=0, column=2, padx=10)

        # Botón de salir
        boton_salir = tk.Button(frame_botones, text="Salir", bg="#95A5A6", fg="white", font=("Arial", 12), command=ventana_productos.destroy)
        boton_salir.grid(row=0, column=3, padx=10)
    def actualizar_productos(self, treeview):
        # Limpiar los datos actuales en el treeview
        for item in treeview.get_children():
            treeview.delete(item)

        # Volver a obtener los datos actualizados de la base de datos
        self.conexion_bd.conectar()

        try:
            # Consulta SQL para obtener los datos actualizados de la tabla productos
            query = """
            SELECT id_producto, nombre, categoria, precio, cantidad, descripcion FROM productos
            """
            self.conexion_bd.cursor.execute(query)
            productos = self.conexion_bd.cursor.fetchall()

            # Agregar los productos al treeview
            for producto in productos:
                treeview.insert("", "end", values=producto)

        except pymysql.MySQLError as e:
            print(f"Error al obtener productos: {e}")
            messagebox.showerror("Error", "No se pudieron obtener los datos de los productos.")

        finally:
            self.conexion_bd.cerrar()
    def abrir_ventana_nuevo_producto(self, treeview):
        """Función para abrir la ventana para agregar un nuevo producto"""
        ventana_nuevo_producto = tk.Toplevel(self.ventana_dashboard)
        ventana_nuevo_producto.title("Nuevo Producto")
        ventana_nuevo_producto.geometry("400x500")

        label_nombre = tk.Label(ventana_nuevo_producto, text="Nombre:")
        label_nombre.pack(pady=10)
        entry_nombre = tk.Entry(ventana_nuevo_producto)
        entry_nombre.pack(pady=10)

        label_categoria = tk.Label(ventana_nuevo_producto, text="Categoría:")
        label_categoria.pack(pady=10)
        entry_categoria = tk.Entry(ventana_nuevo_producto)
        entry_categoria.pack(pady=10)

        label_precio = tk.Label(ventana_nuevo_producto, text="Precio:")
        label_precio.pack(pady=10)
        entry_precio = tk.Entry(ventana_nuevo_producto)
        entry_precio.pack(pady=10)

        label_cantidad = tk.Label(ventana_nuevo_producto, text="Cantidad:")
        label_cantidad.pack(pady=10)
        entry_cantidad = tk.Entry(ventana_nuevo_producto)
        entry_cantidad.pack(pady=10)

        label_descripcion = tk.Label(ventana_nuevo_producto, text="Descripción:")
        label_descripcion.pack(pady=10)
        entry_descripcion = tk.Entry(ventana_nuevo_producto)
        entry_descripcion.pack(pady=10)

        def guardar_nuevo_producto():
            nombre = entry_nombre.get()
            categoria = entry_categoria.get()
            precio = entry_precio.get()
            cantidad = entry_cantidad.get()
            descripcion = entry_descripcion.get()

            if nombre and categoria and precio and cantidad and descripcion:
                try:
                    self.conexion_bd.conectar()
                    query_insertar = """
                    INSERT INTO productos (nombre, categoria, precio, cantidad, descripcion)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    self.conexion_bd.cursor.execute(query_insertar, (nombre, categoria, precio, cantidad, descripcion))
                    self.conexion_bd.conn.commit()
                    messagebox.showinfo("Éxito", "Nuevo producto agregado.")
                    ventana_nuevo_producto.destroy()

                    # Aquí se llama a la función para actualizar el treeview de la ventana principal
                    self.actualizar_productos(treeview)  # Recargar la lista de productos
                except pymysql.MySQLError as e:
                    print(f"Error al agregar el producto: {e}")
                    messagebox.showerror("Error", "Hubo un problema al agregar el producto.")

        boton_guardar = tk.Button(ventana_nuevo_producto, text="Guardar", command=guardar_nuevo_producto)
        boton_guardar.pack(pady=20)
    def eliminar_producto(self, treeview):
        selected_items = treeview.selection()
        if not selected_items:
            messagebox.showerror("Error", "Por favor seleccione un producto para eliminar.")
            return

        selected_item = selected_items[0]
        id_producto = treeview.item(selected_item)['values'][0]

        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este producto?")
        if respuesta:
            self.conexion_bd.conectar()
            try:
                query = "DELETE FROM productos WHERE id_producto = %s"
                self.conexion_bd.cursor.execute(query, (id_producto,))
                self.conexion_bd.conn.commit()
                messagebox.showinfo("Éxito", "Producto eliminado exitosamente.")
                self.actualizar_productos(treeview)  # Recargar la lista de productos
            except pymysql.MySQLError as e:
                print(f"Error al eliminar el producto: {e}")
                messagebox.showerror("Error", "Hubo un problema al eliminar el producto.")
    def editar_producto(self, treeview):
        selected_items = treeview.selection()
        if not selected_items:
            messagebox.showerror("Error", "Por favor seleccione un producto para editar.")
            return

        selected_item = selected_items[0]
        id_producto = treeview.item(selected_item)['values'][0]
        nombre = treeview.item(selected_item)['values'][1]
        categoria = treeview.item(selected_item)['values'][2]
        precio = treeview.item(selected_item)['values'][3]
        cantidad = treeview.item(selected_item)['values'][4]
        descripcion = treeview.item(selected_item)['values'][5]

        # Crear la ventana de edición
        ventana_editar = tk.Toplevel(self.ventana_dashboard)
        ventana_editar.title("Editar Producto")
        ventana_editar.geometry("400x500")

        label_nombre = tk.Label(ventana_editar, text="Nombre:")
        label_nombre.pack(pady=10)
        entry_nombre = tk.Entry(ventana_editar)
        entry_nombre.insert(0, nombre)  # Rellenar con el valor actual
        entry_nombre.pack(pady=10)

        label_categoria = tk.Label(ventana_editar, text="Categoría:")
        label_categoria.pack(pady=10)
        entry_categoria = tk.Entry(ventana_editar)
        entry_categoria.insert(0, categoria)  # Rellenar con el valor actual
        entry_categoria.pack(pady=10)

        label_precio = tk.Label(ventana_editar, text="Precio:")
        label_precio.pack(pady=10)
        entry_precio = tk.Entry(ventana_editar)
        entry_precio.insert(0, precio)  # Rellenar con el valor actual
        entry_precio.pack(pady=10)

        label_cantidad = tk.Label(ventana_editar, text="Cantidad:")
        label_cantidad.pack(pady=10)
        entry_cantidad = tk.Entry(ventana_editar)
        entry_cantidad.insert(0, cantidad)  # Rellenar con el valor actual
        entry_cantidad.pack(pady=10)

        label_descripcion = tk.Label(ventana_editar, text="Descripción:")
        label_descripcion.pack(pady=10)
        entry_descripcion = tk.Entry(ventana_editar)
        entry_descripcion.insert(0, descripcion)  # Rellenar con el valor actual
        entry_descripcion.pack(pady=10)

        def guardar_edicion():
            # Obtener los nuevos valores
            nuevo_nombre = entry_nombre.get()
            nueva_categoria = entry_categoria.get()
            nuevo_precio = entry_precio.get()
            nueva_cantidad = entry_cantidad.get()
            nueva_descripcion = entry_descripcion.get()

            # Actualizar en la base de datos
            if nuevo_nombre and nueva_categoria and nuevo_precio and nueva_cantidad and nueva_descripcion:
                try:
                    self.conexion_bd.conectar()
                    query_actualizar = """
                    UPDATE productos
                    SET nombre = %s, categoria = %s, precio = %s, cantidad = %s, descripcion = %s
                    WHERE id_producto = %s
                    """
                    self.conexion_bd.cursor.execute(query_actualizar, (nuevo_nombre, nueva_categoria, nuevo_precio, nueva_cantidad, nueva_descripcion, id_producto))
                    self.conexion_bd.conn.commit()
                    messagebox.showinfo("Éxito", "Producto actualizado.")
                    ventana_editar.destroy()
                    self.actualizar_productos(treeview)  # Recargar los datos en el Treeview
                except pymysql.MySQLError as e:
                    print(f"Error al actualizar el producto: {e}")
                    messagebox.showerror("Error", "Hubo un problema al actualizar los datos.")

        # Botón para guardar la edición
        boton_guardar = tk.Button(ventana_editar, text="Guardar", command=guardar_edicion)
        boton_guardar.pack(pady=20)

# ------------------------------
# Clase VentanaRegistro
# ------------------------------
class VentanaRegistro(VentanaBase):
    def __init__(self, root, conexion_bd):
        super().__init__(root)
        self.conexion_bd = conexion_bd
        self.root.title("Registro de Usuario")
        self.root.geometry("400x300")

        # Campo para Nombre
        self.label_registro_nombre = tk.Label(self.root, text="Nombre:")
        self.label_registro_nombre.pack(pady=5)

        self.entry_registro_nombre = tk.Entry(self.root)
        self.entry_registro_nombre.pack(pady=5)

        # Campo para Apellido
        self.label_registro_apellido = tk.Label(self.root, text="Apellido:")
        self.label_registro_apellido.pack(pady=5)

        self.entry_registro_apellido = tk.Entry(self.root)
        self.entry_registro_apellido.pack(pady=5)

        # Campo para Nombre de Usuario
        self.label_registro_usuario = tk.Label(self.root, text="Nombre de usuario:")
        self.label_registro_usuario.pack(pady=5)

        self.entry_registro_usuario = tk.Entry(self.root)
        self.entry_registro_usuario.pack(pady=5)

        # Campo para Contraseña
        self.label_registro_contrasena = tk.Label(self.root, text="Contraseña:")
        self.label_registro_contrasena.pack(pady=5)

        self.entry_registro_contrasena = tk.Entry(self.root, show="*")
        self.entry_registro_contrasena.pack(pady=5)

        # Botón de Registrar
        self.boton_registrar = tk.Button(self.root, text="Registrar", command=self.registrar_usuario)
        self.boton_registrar.pack(pady=10)

    def registrar_usuario(self):
        nombre = self.entry_registro_nombre.get()
        apellido = self.entry_registro_apellido.get()
        nombre_usuario = self.entry_registro_usuario.get()
        contrasena = self.entry_registro_contrasena.get()

        nuevo_usuario = Usuario(nombre_usuario, nombre, contrasena, "Usuario", "Activo")
        nuevo_usuario.registrar_usuario(self.conexion_bd)
        messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente.")
        self.root.destroy()  # Cerrar la ventana de registro

# ------------------------------
# ejecución
# ------------------------------
def on_closing():
    # Este método se llamará al intentar cerrar la ventana
    print("Se intentó cerrar la ventana")
    # Aquí puedes mostrar un mensaje de confirmación o realizar alguna otra acción antes de cerrar
    respuesta = tk.messagebox.askokcancel("Cerrar", "¿Estás seguro de que quieres salir?")
    if respuesta:
        root.destroy()  # Si la respuesta es afirmativa, se cierra la ventana
    else:
        return  # Si la respuesta es negativa, no hace nada (la ventana permanece abierta)

if __name__ == "__main__":
    root = tk.Tk()
    # Interceptar el evento de cierre de la ventana (clic en la "X")
    root.protocol("WM_DELETE_WINDOW", on_closing)
    # Conexión a la base e datos
    conexion = ConexionBD("almacenitla-db.ctam6uiuy8ez.us-east-1.rds.amazonaws.com", "estuditlafinal", "itla123.", "almacenadol_db")
    # Crear y mostrar la ventana de login
    ventana_login = VentanaLogin(root, conexion)
    # Iniciar el bucle principal de la interfaz
    root.mainloop()