# Excepciones
# Programacion-213023---Grupo-213023A_2204

"""
Jerarquía de excepciones personalizadas del sistema
Organizadas por categorías: base, validación, operación, datos, configuración
"""

# ---------------------------
# Excepción Base del Sistema
# ---------------------------
class ErrorSistema(Exception):
    """Excepción base para todos los errores del sistema."""
    codigo: int
    mensaje: str

    def __init__(self, mensaje: str, codigo: int = 1000) -> None:
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[Código {codigo}] {mensaje}")


# ===========================
# Errores de Validación
# ===========================

class ErrorValidacion(ErrorSistema):
    """Errores relacionados con validación de datos y entradas."""
    def __init__(self, mensaje: str, codigo: int = 2000) -> None:
        super().__init__(mensaje, codigo)


class DatoInvalidoError(ErrorValidacion):
    """Tipo o formato de dato incorrecto."""
    def __init__(self, campo: str, valor: str) -> None:
        super().__init__(f"El valor '{valor}' no es válido para el campo '{campo}'", 2001)


class DatoFaltanteError(ErrorValidacion):
    """Campo o dato requerido no proporcionado."""
    def __init__(self, campo: str) -> None:
        super().__init__(f"Falta el dato requerido: '{campo}'", 2002)


class LongitudInvalidaError(ErrorValidacion):
    """Valor fuera del rango de longitud permitido."""
    def __init__(self, campo: str, minimo: int, maximo: int) -> None:
        super().__init__(f"'{campo}' debe tener entre {minimo} y {maximo} caracteres", 2003)


# ================================
#  Errores de Operación / Proceso
# ================================

class ErrorOperacion(ErrorSistema):
    """Errores durante la ejecución de una operación o proceso."""
    def __init__(self, mensaje: str, codigo: int = 3000) -> None:
        super().__init__(mensaje, codigo)


class OperacionNoPermitidaError(ErrorOperacion):
    """Intento de realizar una acción sin permisos suficientes."""
    def __init__(self, operacion: str, usuario: str) -> None:
        super().__init__(f"El usuario '{usuario}' no tiene permiso para realizar: {operacion}", 3001)


class EstadoInvalidoError(ErrorOperacion):
    """La entidad no se encuentra en un estado válido para la operación."""
    def __init__(self, entidad: str, estado_actual: str) -> None:
        super().__init__(f"'{entidad}' se encuentra en estado no válido: {estado_actual}", 3002)


class TiempoEjecucionExcedidoError(ErrorOperacion):
    """La operación excedió el tiempo límite de ejecución."""
    def __init__(self, operacion: str, limite_segundos: int) -> None:
        super().__init__(f"La operación '{operacion}' excedió el límite de {limite_segundos}s", 3003)


# ===================================
#  Errores de Datos y Almacenamiento
# ===================================

class ErrorDatos(ErrorSistema):
    """Errores al acceder, leer o escribir datos."""
    def __init__(self, mensaje: str, codigo: int = 4000) -> None:
        super().__init__(mensaje, codigo)


class RegistroNoEncontradoError(ErrorDatos):
    """El registro solicitado no existe en el almacenamiento."""
    def __init__(self, recurso: str, identificador: str) -> None:
        super().__init__(f"No se encontró '{recurso}' con identificador: {identificador}", 4001)


class DuplicadoRegistroError(ErrorDatos):
    """Intento de crear un registro que ya existe."""
    def __init__(self, recurso: str, campo: str, valor: str) -> None:
        super().__init__(f"Ya existe un '{recurso}' con {campo} = '{valor}'", 4002)


class ErrorConexionAlmacenamientoError(ErrorDatos):
    """Fallo al conectar con el origen de datos."""
    def __init__(self, origen: str, motivo: str = "Error desconocido") -> None:
        super().__init__(f"No se pudo conectar a '{origen}': {motivo}", 4003)


# ==========================
#  Errores de Configuración
# ==========================

class ErrorConfiguracion(ErrorSistema):
    """Problemas con la configuración del sistema."""
    def __init__(self, mensaje: str, codigo: int = 5000) -> None:
        super().__init__(mensaje, codigo)


class ParametroNoDefinidoError(ErrorConfiguracion):
    """Falta un parámetro de configuración obligatorio."""
    def __init__(self, parametro: str) -> None:
        super().__init__(f"Parámetro de configuración no definido: '{parametro}'", 5001)
