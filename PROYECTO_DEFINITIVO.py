import datetime
inventario = {}
prestamos = {"sala": {}, "casa": {}}
prestamos_usuarios = {}
libros = []

# Función para añadir libros al inventario
def anadir_libro(titulo, autor, cantidad, genero):
    libro = {
        "titulo": titulo,
        "autor": autor,
        "cantidad_total": cantidad,
        "cantidad_disponible": cantidad,
        "genero": genero,
        "prestamos": []  # Lista de préstamos con detalles
    }
    libros.append(libro)
    print(f"Libro '{titulo}' se ha añadido exitosamente.")
# Función para agregar libros al inventario
def agregar_libro(titulo, autor, cantidad, genero):
    if titulo not in inventario:
        inventario[titulo] = {"cantidad": cantidad, "genero": genero, "autor": autor, "prestamos": []}
    else:
        inventario[titulo]["cantidad"] += cantidad
    anadir_libro(titulo, autor, cantidad, genero)
# Función para consultar todos los libros del inventario
def consultar_libros():
    print("\nLibros en Inventario:\n")
    for libro in libros:
        print(f"Titulo: {libro['titulo']}, Autor: {libro['autor']}, Género: {libro['genero']}, "
              f"Disponibles: {libro['cantidad_disponible']} de {libro['cantidad_total']}")

# Función para consultar libros en préstamo de un usuario
def consultar_prestamos(usuario):
    print(f"\nLibros en préstamo para el usuario '{usuario}':\n")
    encontrado = False
    for libro in libros:
        for prestamo in libro["prestamos"]:
            if prestamo["usuario"] == usuario:
                encontrado = True
                print(f"- {libro['titulo']}: Fecha de devolución: {prestamo['fecha_prestamo']}, "
                      f"Renovaciones: {prestamo['renovaciones']}")
    if not encontrado:
        print("No tienes libros en préstamo.\n")

# Función para prestar un libro
def prestar_libro(titulo, tipo, usuario):
    if titulo not in inventario or inventario[titulo]["cantidad"] <= 0:
        return f"El libro '{titulo}' no está disponible en este momento."

    if tipo not in prestamos:
        return f"Tipo de préstamo '{tipo}' no válido."

    # Verificar si el usuario ya tiene 3 libros prestados
    if usuario in prestamos_usuarios and len(prestamos_usuarios[usuario]) >= 3:
        return f"No puedes pedir más de 3 libros prestados. Devuelve alguno antes de solicitar otro."

    # Reducir cantidad del inventario y registrar préstamo
    inventario[titulo]["cantidad"] -= 1
    prestamos.setdefault(tipo, {}).setdefault(titulo, []).append(usuario)
    prestamos_usuarios.setdefault(usuario, []).append(titulo)

    # Registrar préstamo en la lista de libros
    for libro in libros:
        if libro["titulo"] == titulo:
            fecha_devolucion = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            libro["cantidad_disponible"] -= 1
            libro["prestamos"].append({
                "usuario": usuario,
                "fecha_prestamo": fecha_devolucion,
                "renovaciones": 0,
                "tipo": tipo
            })
            break
    return f"Préstamo de '{titulo}' registrado para {tipo}."
# Estructura para solicitudes de préstamo
solicitudes_prestamo = {} # Estructura central para gestionar todas las solicitudes de préstamo. Se utiliza en las funciones `solicitar_prestamo_libro` y `gestionar_solicitudes_prestamo`.

# Función para devolver un libro
def devolver_libro(titulo, usuario):
    if titulo in inventario:
        inventario[titulo]["cantidad"] += 1

        # Eliminar el libro del registro del usuario
        if usuario in prestamos_usuarios and titulo in prestamos_usuarios[usuario]:
            prestamos_usuarios[usuario].remove(titulo)

        # Eliminar el usuario del préstamo si ya no tiene ese libro
        for tipo, prestamos_por_tipo in prestamos.items():
            if titulo in prestamos_por_tipo and usuario in prestamos_por_tipo[titulo]:
                prestamos_por_tipo[titulo].remove(usuario)
                if not prestamos_por_tipo[titulo]:
                    del prestamos_por_tipo[titulo]

        # Actualizar los libros
        for libro in libros:
            if libro["titulo"] == titulo:
                libro["cantidad_disponible"] += 1
                libro["prestamos"] = [p for p in libro["prestamos"] if p["usuario"] != usuario]
                break
        return f"Se ha devuelto el libro '{titulo}'."
    else:
        return f"El libro '{titulo}' no pertenece al inventario."
    
# Función para mostrar el inventario
def mostrar_inventario():
    if not inventario:
        print("El inventario está vacío.")
        return

    for titulo, datos in inventario.items():
        print(f"Título: {titulo}, Autor: {datos['autor']}, Género: {datos['genero']}, Cantidad: {datos['cantidad']}")

# Función para filtrar libros por género o autor
def filtrar_libros(genero=None, autor=None):
    resultados = [
        {"titulo": titulo, **datos}
        for titulo, datos in inventario.items()
        if (genero is None or datos["genero"] == genero) and (autor is None or datos["autor"] == autor)
    ]
    return resultados

# Función para consultar libros y prestar
def consultar_y_prestar_libros(usuario):
    global tipo
    genero = input("Ingresa un género para filtrar (o deja en blanco para todos): ").title()
    autor = input("Ingresa un autor para filtrar (o deja en blanco para todos): ").title()
    filtros = filtrar_libros(genero=genero or None, autor=autor or None)

    if not filtros:
        print("No se encontraron libros.")
        return

    for i, libro in enumerate(filtros, start=1):
        print(f"{i}. Título: {libro['titulo']}, Autor: {libro['autor']}, Género: {libro['genero']}, Cantidad: {libro['cantidad']}")

    seleccion = input("Selecciona el número del libro para más detalles o presiona Enter para regresar: ")
    if seleccion.isdigit():
        indice = int(seleccion) - 1
        if 0 <= indice < len(filtros):
            titulo_seleccionado = filtros[indice]['titulo']

            confirmacion = input(f"Has seleccionado: {titulo_seleccionado}. ¿Deseas continuar con el préstamo? (si/no): ").lower()
            confirmacion.strip()
            if confirmacion != "si":
                print("Solicitud cancelada.")
                return

            tipo = input("¿Deseas el libro para 'sala' o 'casa'?: ").lower()
            tipo.strip()
            while tipo not in ["sala", "casa"]:
                tipo = input("Por favor, selecciona 'sala' o 'casa': ").lower()
                tipo.strip()
            solicitudes_prestamo.setdefault(titulo_seleccionado, []).append(usuario)
            print(f"La solicitud del libro '{titulo_seleccionado}' ha sido realizada. Espera la aprobación del trabajador.")
        else:
            print("Selección no válida.")
    else:
        print("Volviendo al menú principal.")

def gestionar_solicitudes_prestamo():
    print("\n--- Solicitudes de Préstamo ---")
    if not solicitudes_prestamo:
        print("No hay solicitudes pendientes.")
        return

    for titulo, usuarios_solicitantes in list(solicitudes_prestamo.items()):
        print(f"Libro: {titulo}")
        for usuario in usuarios_solicitantes[:]:
            print(f"- Usuario: {usuario}")
            aprobar = input(f"¿Aprobar solicitud de {usuario} para '{titulo}'? (sí/no): ").lower()
            if aprobar == "sí":
                if titulo in inventario and inventario[titulo]["cantidad"] > 0:
                    resultado = prestar_libro(titulo, tipo, usuario)
                    print(resultado)
                    if "registrado" in resultado:
                        inventario[titulo]["cantidad"] -= 1
                        usuarios_solicitantes.remove(usuario)
                    else:
                        print("Error al registrar el préstamo.")
                else:
                    print(f"No se puede aprobar la solicitud. El libro '{titulo}' no está disponible.")

        # Eliminar solicitudes vacías
        if not solicitudes_prestamo[titulo]:
            del solicitudes_prestamo[titulo]

# Función para renovar préstamos
def renovar_prestamo(usuario, titulo_libro):
    for libro in libros:
        if libro["titulo"] == titulo_libro:
            for prestamo in libro["prestamos"]:
                if prestamo["usuario"] == usuario:
                    if prestamo["renovaciones"] < 2:
                        prestamo["renovaciones"] += 1
                        nueva_fecha = (datetime.datetime.strptime(prestamo["fecha_prestamo"], "%Y-%m-%d") 
                                       + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
                        prestamo["fecha_prestamo"] = nueva_fecha
                        print(f"El préstamo del libro '{titulo_libro}' ha sido renovado. Nueva fecha de devolución: {nueva_fecha}")
                    else:
                        print(f"No puedes renovar el libro '{titulo_libro}' más de 2 veces.")
                    return
            print(f"No tienes el libro '{titulo_libro}' en préstamo.")
            return
    print(f"El libro '{titulo_libro}' no existe en el inventario.")

def gestionar_entrega_libros():
    print("\n--- Entrega de Libros ---")
    entregas = False
    for libro in libros:
        for prestamo in libro["prestamos"][:]:
            entregas = True
            print(f"Libro: {libro['titulo']}, Usuario: {prestamo['usuario']}, Fecha de devolución: {prestamo['fecha_prestamo']}")
            confirmar_entrega = input(f"¿Confirmar entrega del libro '{libro['titulo']}' por parte del usuario {prestamo['usuario']}? (sí/no): ").lower()
            if confirmar_entrega == "sí":
                libro["cantidad_disponible"] += 1
                libro["prestamos"].remove(prestamo)
                print(f"Entrega del libro '{libro['titulo']}' confirmada y actualizada en el inventario.")
    if not entregas:
        print("No hay libros pendientes de entrega.")

# Menú para usuarios
def menu_usuario(usuario):
    while True:
        print(f"\n--- Menú Usuario: {usuario} ---")
        print("1. Consultar libros disponibles y solicitar prestamo")
        print("2. Consultar libros en préstamo")
        print("3. Devolver libro")
        print("4. Renovar un préstamo")
        print("5. Cambiar mi contraseña")
        print("6. Eliminar cuenta")
        print("7. Cerrar sesión")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            consultar_y_prestar_libros(usuario)
        elif opcion == "2":
            consultar_prestamos(usuario)
        elif opcion == "3":
            titulo = input("Ingresa el título del libro que deseas devolver: ")
            print(devolver_libro(titulo, usuario))
        elif opcion == "4":
            titulo = input("Ingresa el título del libro que deseas renovar: ")
            renovar_prestamo(usuario, titulo)
        elif opcion == "5":
            cambiar_contraseña(usuario)
        elif opcion == "6":
            tiene_prestamos_sala = any(
                prestamo["usuario"] == usuario and prestamo["tipo"] == "casa" or prestamo["tipo"] == "sala"
                for libro in libros
                for prestamo in libro["prestamos"]
            )
            if tiene_prestamos_sala:
                print("No puedes cerrar eliminar la cuenta mientras tengas libros prestados.")
            else:
                eliminar_mi_cuenta()
                return
        elif opcion == "7":
            # Validar si hay préstamos en sala sin devolver
            tiene_prestamos_sala = any(
                prestamo["usuario"] == usuario and prestamo["tipo"] == "sala"
                for libro in libros
                for prestamo in libro["prestamos"]
            )
            if tiene_prestamos_sala:
                print("No puedes cerrar sesión mientras tengas libros prestados para sala.")
            else:
                print("Cerrando sesión...")
                break
        else:
            print("Opción no válida, intenta nuevamente.")

def validar_contraseña_fuerte(contraseña, telefono):
    tiene_mayuscula = any(c.isupper() for c in contraseña)
    tiene_minuscula = any(c.islower() for c in contraseña)
    tiene_numero = any(c.isdigit() for c in contraseña)
    tiene_longitud_minima = len(contraseña) >= 4
    # tiene_10_numeros = len(telefono) = 10
    
    if not tiene_longitud_minima:
        return False, "La contraseña debe tener al menos 4 caracteres."
    if not tiene_mayuscula:
        return False, "La contraseña debe contener al menos una letra mayúscula."
    if not tiene_minuscula:
        return False, "La contraseña debe contener al menos una letra minúscula."
    if not tiene_numero:
        return False, "La contraseña debe contener al menos un número."
    
    return True, ""

# Crear usuario
def crear_usuario():
    usuario = input("Ingrese un nombre del usuario: ")
    
    if usuario in usuarios:
        print("El usuario ya existe. Intente con otro nombre.")
        return
    
    while True:
        contraseña = input("Ingrese una contraseña: ") 
        confirmar_contraseña = input("Confirme la contraseña: ")
        
        if contraseña != confirmar_contraseña:
            print("Las contraseñas no coinciden. Intente de nuevo.")
            continue
        
        # Validar la contraseña
        es_valida, mensaje = validar_contraseña_fuerte(contraseña)
        if not es_valida:
            print(f"Contraseña no válida: {mensaje}")
            continue
        break
    

    telefono = input("Ingrese su numero: ") 

    
    usuarios[usuario] = {"contraseña": contraseña, "perfil": "usuario", "telefono": telefono}
    print(f"Usuario {usuario} creado exitosamente.")
    
# Actualizar usuario

def actualizar_usuario():
    usuario = input("Ingrese el nombre de usuario a modificar: ")
    
    if usuario not in usuarios or usuarios[usuario]["perfil"] != "usuario":
        print("El empleado no existe.")
        return
    
    telefono = input("Ingrese el nuevo número de teléfono: ").strip()
    
    usuarios[usuario]["telefono"] = telefono
    print(f"Teléfono del usuario {usuario} actualizado exitosamente.")
    
# Eliminar usuario

def eliminar_usuario():
    usuario = input("Ingrese el nombre del usuario a eliminar: ")
    
    if usuario not in usuarios or usuarios[usuario]["perfil"] != "usuario":
        print("El usuario no existe.")
        return
    tiene_prestamos_sala = any(
        prestamo["usuario"] == usuario and prestamo["tipo"] == "casa" or prestamo["tipo"] == "sala"
        for libro in libros
        for prestamo in libro["prestamos"]
    )
    if tiene_prestamos_sala:
        print("No puedes eliminar el usuario mientras tenga libros prestados.")
    else:
        del usuarios[usuario]
        print(f"Usuario {usuario} eliminado exitosamente.")
        return
    
    
# Ver los usuarios existentes y registrados

def ver_usuarios():
    print("\n--- Usuarios Registrados ---")
    usuarios_registrados = [
        (usuario, datos["telefono"], datos["perfil"]) 
        for usuario, datos in usuarios.items() 
        if datos["perfil"] == "usuario"
    ]
    
    if usuarios_registrados:
        for usuario, telefono, perfil in usuarios_registrados:
            print(f"Usuario: {usuario}, Teléfono: {telefono}, Perfil: {perfil}")
    else:
        print("No hay usuarios registrados.")
   
# CRUD usuarios
def info_usuarios():
    while True:
        print("Bienvenido a la info de usuarios")
        print("1. Crear usuario")
        print("2. Actualizar usuario")
        print("3. Eliminar usuario")
        print("4. Ver los usuarios registrados")
        print("5. Volver")
        
        opcion = input("¿Que accion desea realizar?:") 
        
        if opcion == "1":
            crear_usuario()
        elif opcion == "2":
            actualizar_usuario()
        elif opcion == "3":
            eliminar_usuario()
        elif opcion == "4":
            ver_usuarios()
        elif opcion == "5":
            break
# actualiza su cuenta
def actualizar_mi_cuenta():
    print("\n--- Actualizar Mi Cuenta ---")
    usuario = input("Introduce tu nombre de usuario: ")

    if usuario not in usuarios:
        print("El usuario no existe.")
        return

    telefono_actual = input("Introduce tu telefono actual para continuar: ")
    if telefono_actual != usuarios[usuario]["telefono"]:
        print("El número de teléfono no coincide.")
        return

    if usuarios[usuario]["telefono"] == telefono_actual:
        nuevo_usuario = input("Introduce un nuevo nombre de usuario (deja en blanco si no deseas cambiarlo): ")
        while True:
            nueva_contraseña = input("Ingrese la nueva contraseña: ")
            confirmar_contraseña = input("Confirme la nueva contraseña: ")
        
            if nueva_contraseña != confirmar_contraseña:
                print("Las contraseñas no coinciden. Intente de nuevo.")
                continue
        
            es_valida, mensaje = validar_contraseña_fuerte(nueva_contraseña)
            if not es_valida:
                print(f"Contraseña no válida: {mensaje}")
                continue
            break
        
        if nuevo_usuario:
            usuarios[nuevo_usuario] = usuarios.pop(usuario)
            usuario = nuevo_usuario  

        if nueva_contraseña:
            usuarios[usuario]["contraseña"] = nueva_contraseña

        print("Cuenta actualizada con éxito.")
    else:
        print("Contraseña incorrecta. No se pudo actualizar la cuenta.")


# Eliminar cuenta según la contraseña
def eliminar():
    while True:
        contraseña = input("Escribe tu contraseña: ")

        usuario_a_eliminar = None
        for usuario, datos in usuarios.items():
            if datos["contraseña"] == contraseña:
                usuario_a_eliminar = usuario
                break
        
        if usuario_a_eliminar:
            del usuarios[usuario_a_eliminar]
            print("Usuario eliminado exitosamente.")
            break
            
        else:
            print("Contraseña incorrecta o usuario no encontrado.")

# Confirmación para eliminar cuenta
def eliminar_mi_cuenta():
    while True:
        print("ADVERTENCIA")
        print("1. Sí")
        print("2. No")
        
        opcion = input("¿Estás seguro de querer eliminar tu cuenta?:")
        
        if opcion == "1":
            eliminar()
            print("Cuenta eliminada con exito, regresando al menu princiapl...")
            return True            
        elif opcion == "2":
            menu_trabajador()
            return False 
        else:
            print("Ingrese una opción válida.")
                
# CRUD mi cuenta(empleado)

def mi_cuenta():
    
    print("Bienvenido a las opciones de tu propia cuenta")
    print("1. Eliminar cuenta")
    print("2. Actualizar cuenta")
    print("3. Volver")
        
    opcion = input("¿Que deseas hacer?:")
        
    if opcion == "1":
        eliminar_mi_cuenta()
        return True    
        
    elif opcion == "2":
        actualizar_mi_cuenta()
            
    elif opcion=="3":
        return False
        
# Menú para empleados
def menu_trabajador():
    while True:
        print("\n--- Menú Trabajador ---")
        print("1. Añadir libro")
        print("2. Consultar libros")
        print("3. Solicitudes de préstamo de usuarios")
        print("4. Entrega de libros de los usuarios")
        print("5. Acerca de los usuarios")
        print("6. Sobre mi cuenta")
        print("7. Cerrar sesión")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            titulo = input("Título del libro: ")
            autor = input("Autor del libro: ")
            try:
                cantidad = int(input("Cantidad disponible: "))
                if cantidad < 0:
                    raise ValueError("La cantidad no puede ser negativa.")
            except ValueError as e:
                print(f"Entrada inválida: {e}")
                continue
            genero = input("Género del libro: ")
            anadir_libro(titulo, autor, cantidad, genero)
        elif opcion == "2":
            consultar_libros()
        elif opcion == "3":
            gestionar_solicitudes_prestamo()
        elif opcion == "4":
            gestionar_entrega_libros()
        elif opcion == "5":
            info_usuarios()
        elif opcion == "6":
            if mi_cuenta():
                return
        elif opcion == "7":
            print("Cerrando sesión...")
            break
        else:
            print("Opción no válida, intenta nuevamente.")

# intento de base de datos
usuarios = {"": {"contraseña": "", "perfil": "", "telefono": ""},
}
# Inicio de la aplicación
def menu_principal():
    while True:
        print("\n--- Sistema de Biblioteca ---")
        print("1. Iniciar Sesión")
        print("2. Crear Cuenta")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            iniciar_sesion()
        elif opcion == "2":
            crear_cuenta()
        elif opcion == "3":
            print("¡Hasta luego!")
            break

        else:
            print("Opción no válida, intente de nuevo.")
##########################################################################################
#Iniciar sesión
def iniciar_sesion():
    usuario = input("Usuario: ")
    contraseña = input("Contraseña: ")
    
    if usuario in usuarios and usuarios[usuario]["contraseña"] == contraseña:
        print(f"Bienvenido {usuario}! Perfil: {usuarios[usuario]['perfil']}")
        if usuarios[usuario]["perfil"] == "administrador":
            menu_admin(usuario)
        elif usuarios[usuario]["perfil"] == "empleado":
            menu_trabajador()
        else:
            menu_usuario(usuario)
    else:
        print("Usuario o contraseña incorrectos.")

######################################################################################
#Crear cuenta
def crear_cuenta():
    usuario = input("Ingrese un nombre de usuario: ")
    
    if usuario in usuarios:
        print("El usuario ya existe. Intente con otro nombre.")
        return
    
    while True:
        contraseña = input("Ingrese una contraseña: ") 
        confirmar_contraseña = input("Confirme la contraseña: ")
        
        if contraseña != confirmar_contraseña:
            print("Las contraseñas no coinciden. Intente de nuevo.")
            continue
        
        # Validar la contraseña
        es_valida, mensaje = validar_contraseña_fuerte(contraseña)
        if not es_valida:
            print(f"Contraseña no válida: {mensaje}")
            continue
        break
    
    telefono = input("Ingrese su número de teléfono: ")
    
    print("\nSeleccione el perfil para la cuenta:")
    print("1. Usuario")
    print("2. Empleado")
    print("3. Administrador")
    perfil_opcion = input("Seleccione una opción: ")
    
    if perfil_opcion == "1":
        perfil = "usuario"
    elif perfil_opcion == "2":
        perfil = "empleado"
    elif perfil_opcion == "3":
        perfil = "administrador"
        if any(u["perfil"] == "administrador" for u in usuarios.values()):
            print("Ya existe un administrador. No se puede crear otro.")
            return
    else:
        print("Opción no válida. Intente de nuevo.")
        return
    
    usuarios[usuario] = {"contraseña": contraseña, "perfil": perfil, "telefono": telefono}
    print(f"Cuenta creada exitosamente para {usuario} con perfil {perfil}.")

########################################################################################
#Menú de administrador
def menu_admin(usuario_actual):
    while True:
        print("\n--- Menú Administrador ---")
        print("1. Ver todos los empleados")
        print("2. Crear un empleado")
        print("3. Eliminar un empleado")
        print("4. Modificar datos de un empleado")
        print("5. Cambiar mi contraseña")
        print("6. Salir del menú administrador")
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            ver_empleados()
        elif opcion == "2":
            crear_empleado()
        elif opcion == "3":
            eliminar_empleado()
        elif opcion == "4":
            modificar_empleado()
        elif opcion == "5":
            cambiar_contraseña(usuario_actual)
        elif opcion == "6":
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida, intente de nuevo.")
############################################################################################
#Ver todos los empleados y número de teléfono
def ver_empleados():
    print("\n--- Empleados ---")
    empleados = [ (usuario, datos["telefono"]) for usuario, datos in usuarios.items() if datos["perfil"] == "empleado" ]
    if empleados:
        for emp, tel in empleados:
            print(f"Empleado: {emp}, Teléfono: {tel}")
    else:
        print("No hay empleados registrados.")
#########################################################################################3
#Crear un nuevo empleado
def crear_empleado():
    usuario = input("Ingrese un nombre de usuario para el empleado: ")
    
    if usuario in usuarios:
        print("El usuario ya existe. Intente con otro nombre.")
        return
    
    while True:
        contraseña = input("Ingrese una contraseña: ") 
        confirmar_contraseña = input("Confirme la contraseña: ")
        
        if contraseña != confirmar_contraseña:
            print("Las contraseñas no coinciden. Intente de nuevo.")
            continue
        
        # Validar la contraseña
        es_valida, mensaje = validar_contraseña_fuerte(contraseña)
        if not es_valida:
            print(f"Contraseña no válida: {mensaje}")
            continue
        break
    
    telefono = input("Ingrese el número de teléfono del empleado: ")
    
    usuarios[usuario] = {"contraseña": contraseña, "perfil": "empleado", "telefono": telefono}
    print(f"Empleado {usuario} creado exitosamente.")
#######################################################################################
#Eliminar un empleado
def eliminar_empleado():
    usuario = input("Ingrese el nombre de usuario del empleado a eliminar: ")
    
    if usuario not in usuarios or usuarios[usuario]["perfil"] != "empleado":
        print("El empleado no existe.")
        return
    
    del usuarios[usuario]
    print(f"Empleado {usuario} eliminado exitosamente.")
##########################################################################################
#Modificar datos de un empleado
def modificar_empleado():
    usuario = input("Ingrese el nombre de usuario del empleado a modificar: ")
    
    if usuario not in usuarios or usuarios[usuario]["perfil"] != "empleado":
        print("El empleado no existe.")
        return
    
    telefono = input("Ingrese el nuevo número de teléfono: ")
    
    usuarios[usuario]["telefono"] = telefono
    print(f"Teléfono del empleado {usuario} actualizado exitosamente.")

##############################################################################
#Cambiar contraseña
def cambiar_contraseña(usuario):
    telefono = input("Ingrese su número de teléfono: ")
    
    if telefono != usuarios[usuario]["telefono"]:
        print("El número de teléfono no coincide.")
        return
    
    while True:
        nueva_contraseña = input("Ingrese una contraseña: ") 
        confirmar_contraseña = input("Confirme la contraseña: ")
        
        if nueva_contraseña != confirmar_contraseña:
            print("Las contraseñas no coinciden. Intente de nuevo.")
            continue
        
        # Validar la contraseña
        es_valida, mensaje = validar_contraseña_fuerte(nueva_contraseña)
        if not es_valida:
            print(f"Contraseña no válida: {mensaje}")
            continue
        break
    
    usuarios[usuario]["contraseña"] = nueva_contraseña
    print(f"Contraseña de {usuario} modificada exitosamente.")
#Libros por defecto
agregar_libro("Miraculous", "Tomas", 3, "Clásico")
agregar_libro("1984", "George Orwell", 2, "Distopía")
agregar_libro("El Hombre Lobo", "Pedro Riera", 4, "Terror" )
agregar_libro("Cujo", "stephen king", 10, "Terror")
agregar_libro("Amor en tiempos de colera", "GABO", 2, "Literario")
# Inicio del sistema
menu_principal()