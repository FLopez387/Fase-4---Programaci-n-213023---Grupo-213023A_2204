# Registro
# Programacion-213023---Grupo-213023A_2204

"""
Sistema de Registro de Eventos y Ejemplos de Manejo de Excepciones
Configura el archivo de log y muestra patrones:
- try / except
- try / except / else
- try / except / finally
- raise ... from ...
"""

import logging
from datetime import datetime
from excepciones import (
    ErrorSistema, DatoInvalidoError, DatoFaltanteError,
    RegistroNoEncontradoError, DuplicadoRegistroError,
    OperacionNoPermitidaError
)

# =================================================
#  Configuración del sistema de registro (Logging)
# =================================================

def configurar_registro(nombre_archivo: str = "sistema.log") -> logging.Logger:
    """
    Configura el sistema de registro de eventos y errores.
    Guarda la información en un archivo con formato estructurado.
    """
    # Crear el registrador principal
    logger = logging.getLogger("sistema_principal")
    logger.setLevel(logging.DEBUG)  # Registrar desde nivel DEBUG
    logger.propagate = False  # Evitar duplicación de mensajes

    # Formato del registro:
    # Fecha - Nivel - Mensaje - Origen
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s | [en %(module)s:%(lineno)d]",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Manejador para archivo
    manejador_archivo = logging.FileHandler(nombre_archivo, encoding="utf-8")
    manejador_archivo.setFormatter(formato)
    manejador_archivo.setLevel(logging.DEBUG)

    # Manejador para consola
    manejador_consola = logging.StreamHandler()
    manejador_consola.setFormatter(formato)
    manejador_consola.setLevel(logging.INFO)

    # Agregar manejadores al registrador
    logger.addHandler(manejador_archivo)
    logger.addHandler(manejador_consola)

    logger.info(" Sistema de registro inicializado correctamente")
    return logger


# Inicializar el registrador
logger = configurar_registro()


# ===========================================
#  Ejemplos de uso de excepciones y registro
# ===========================================

def ejemplo_try_excepcion_basico(valor: int) -> None:
    """Ejemplo 1: Estructura básica try / except"""
    print("\n--- Ejemplo 1: try / except ---")
    try:
        if valor < 0:
            raise DatoInvalidoError("edad", str(valor))
        print(f" Valor recibido: {valor}")
    except ErrorSistema as e:
        logger.error(f"Se capturó una excepción: {e.mensaje} (Código: {e.codigo})")


def ejemplo_try_except_else(nombre: str) -> None:
    """Ejemplo 2: Estructura try / except / else"""
    print("\n--- Ejemplo 2: try / except / else ---")
    try:
        if not nombre.strip():
            raise DatoFaltanteError("nombre_usuario")
    except ErrorSistema as e:
        logger.warning(f"Validación fallida: {e.mensaje}")
    else:
        # Se ejecuta SOLO si NO hubo excepciones
        logger.info(f"Validación exitosa para usuario: {nombre}")
        print(f" ¡Bienvenido, {nombre}!")


def ejemplo_try_except_finally(identificador: str) -> None:
    """Ejemplo 3: Estructura try / except / finally"""
    print("\n---  Ejemplo 3: try / except / finally ---")
    recurso_abierto = False
    try:
        logger.debug(f"Intentando acceder al recurso: {identificador}")
        recurso_abierto = True
        raise RegistroNoEncontradoError("Producto", identificador)
    except ErrorSistema as e:
        logger.error(f"Error al acceder a recurso: {e.mensaje}")
    finally:
        # Se ejecuta SIEMPRE, haya error o no
        if recurso_abierto:
            logger.debug("Cerrando conexión/recurso...")
            recurso_abierto = False
        print(" Bloque finally ejecutado: Recursos liberados")


def ejemplo_raise_from(dato: dict) -> None:
    """Ejemplo 4: Uso de 'raise NuevaExcepcion from original_excepcion'"""
    print("\n--- Ejemplo 4: raise ... from ... ---")
    try:
        if "id" not in dato:
            raise KeyError("Falta la clave 'id' en los datos")
        if dato["id"] <= 0:
            raise ValueError("El identificador debe ser mayor a cero")
    except KeyError as error_original:
        # Encadenar excepciones: conservar el contexto del error original
        raise DatoFaltanteError("id") from error_original
    except ValueError as error_original:
        raise DatoInvalidoError("id", str(dato["id"])) from error_original


def ejemplo_raise_from_uso() -> None:
    """Prueba del ejemplo 4 con captura externa"""
    try:
        ejemplo_raise_from({"nombre": "Sin Identificador"})
    except ErrorSistema as e:
        logger.error(f"Excepción traducida: {e.mensaje}")
        # __cause__ conserva la excepción original
        if e.__cause__:
            logger.debug(f"↳ Causa original: {repr(e.__cause__)}")


def ejemplo_duplicado_y_permisos() -> None:
    """Ejemplo 5: Otros tipos de excepciones"""
    print("\n--- Ejemplo 5: Otras excepciones personalizadas ---")
    try:
        raise DuplicadoRegistroError("Usuario", "correo", "ejemplo@correo.com")
    except DuplicadoRegistroError as e:
        logger.warning(f"Intento de duplicado: {e.mensaje}")

    try:
        raise OperacionNoPermitidaError("eliminar_registros", "usuario_invitado")
    except OperacionNoPermitidaError as e:
        logger.critical(f"Intento de acceso no autorizado: {e.mensaje}")


# ================================
# Ejecución de todos los ejemplos
# ================================

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Iniciando demostración del sistema de excepciones")
    logger.info("=" * 50)

    ejemplo_try_excepcion_basico(-5)
    ejemplo_try_excepcion_basico(25)

    ejemplo_try_except_else("Carlos Pérez")
    ejemplo_try_except_else("")

    ejemplo_try_except_finally("PROD-999")

    ejemplo_duplicado_y_permisos()

    print("\n---  Ejemplo 4 completo con captura ---")
    ejemplo_raise_from_uso()

    logger.info(" Finalización de todos los ejemplos")
    print("\n Revisa el archivo 'sistema.log' para ver el registro completo.")