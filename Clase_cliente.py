# Clase cliente
# Programacion-213023---Grupo-213023A_2204
"""Clase Cliente con encapsulación y validaciones de datos personales."""
import re
import logging
from config_logging import configurar_logging
from FASE_4_excepciones import DatoInvalidoError

# Inicializar sistema de logs
configurar_logging()
logger = logging.getLogger(__name__)


class DatoPersonalInvalidoError(DatoInvalidoError):
    """Excepción específica para datos personales incorrectos."""
    codigo_error = "ERR-CLI-001"
    mensaje = "Uno de los datos personales no es válido"


class Cliente:
    """
    Clase que representa a un cliente del sistema.
    Todos los datos personales están encapsulados con validaciones estrictas.
    """

    # Patrones de validación (expresiones regulares)
    _PATRON_NOMBRE = re.compile(r"^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]{3,100}$")
    _PATRON_IDENTIFICACION = re.compile(r"^[A-Z0-9-]{5,20}$")
    _PATRON_CORREO = re.compile(
        r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
    _PATRON_TELEFONO = re.compile(r"^\+?[0-9\s-]{7,15}$")

    def __init__(
        self,
        identificacion: str,
        nombres: str,
        apellidos: str,
        correo: str,
        telefono: str = "",
        direccion: str = ""
    ):
        # Asignación con validación a través de propiedades
        self.identificacion = identificacion
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.telefono = telefono
        self.direccion = direccion

        logger.info(f"✅ Cliente registrado: {self.identificacion} — {self.nombres_completo}")

    # ===== Propiedades de validación =====

    @property
    def identificacion(self) -> str:
        return self.__identificacion

    @identificacion.setter
    def identificacion(self, valor: str):
        valor_limpio = valor.strip()
        if not self._PATRON_IDENTIFICACION.match(valor_limpio):
            logger.warning(f" Identificación inválida: '{valor}'")
            raise DatoPersonalInvalidoError(
                "La identificación debe tener entre 5 y 20 caracteres y solo permitir letras mayúsculas, números y guiones."
            )
        self.__identificacion = valor_limpio

    @property
    def nombres(self) -> str:
        return self.__nombres

    @nombres.setter
    def nombres(self, valor: str):
        valor_limpio = valor.strip()
        if not self._PATRON_NOMBRE.match(valor_limpio):
            logger.warning(f" Nombres inválidos: '{valor}'")
            raise DatoPersonalInvalidoError(
                "El nombre debe tener entre 3 y 100 caracteres y solo permitir letras y espacios."
            )
        self.__nombres = valor_limpio.title()

    @property
    def apellidos(self) -> str:
        return self.__apellidos

    @apellidos.setter
    def apellidos(self, valor: str):
        valor_limpio = valor.strip()
        if not self._PATRON_NOMBRE.match(valor_limpio):
            logger.warning(f" Apellidos inválidos: '{valor}'")
            raise DatoPersonalInvalidoError(
                "El apellido debe tener entre 3 y 100 caracteres y solo permitir letras y espacios."
            )
        self.__apellidos = valor_limpio.title()

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str):
        valor_limpio = valor.strip().lower()
        if not self._PATRON_CORREO.match(valor_limpio):
            logger.warning(f" Correo inválido: '{valor}'")
            raise DatoPersonalInvalidoError(
                "El correo electrónico no tiene un formato válido. Ejemplo: nombre@dominio.com"
            )
        self.__correo = valor_limpio

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        valor_limpio = valor.strip()
        if valor_limpio and not self._PATRON_TELEFONO.match(valor_limpio):
            logger.warning(f" Teléfono inválido: '{valor}'")
            raise DatoPersonalInvalidoError(
                "El teléfono debe contener solo números, espacios, guiones y opcionalmente un signo '+' al inicio."
            )
        self.__telefono = valor_limpio

    @property
    def direccion(self) -> str:
        return self.__direccion

    @direccion.setter
    def direccion(self, valor: str):
        self.__direccion = valor.strip()

    # ===== Propiedades de uso conveniente =====

    @property
    def nombres_completo(self) -> str:
        """Devuelve el nombre completo formateado."""
        return f"{self.nombres} {self.apellidos}"

    # ===== Métodos seguros =====

    def obtener_datos_publicos(self) -> dict:
        """
        Devuelve solo los datos necesarios para mostrar en listas.
        NO expone información sensible sin consentimiento.
        """
        return {
            "identificacion": self.identificacion,
            "nombre_completo": self.nombres_completo,
            "correo": self.correo
        }

    def __str__(self) -> str:
        """Representación segura: no muestra todos los datos sensibles."""
        return f"Cliente({self.identificacion} — {self.nombres_completo})"

    def __repr__(self) -> str:
        return f"<Cliente: {self.identificacion}>"


# ===== Ejemplos se uso con manejo de excepciones =====

if __name__ == "__main__":
    print("=" * 60)
    print("📦 GESTIÓN DE CLIENTES")
    print("=" * 60)

    #  Ejemplo 1: try / except / else — Creación exitosa
    print("\n--- Prueba 1: Creación de cliente válido ---")
    try:
        cliente1 = Cliente(
            identificacion="CC-1002345678",
            nombres="  maría jose  ",
            apellidos="  gómez pérez  ",
            correo="MARIA@ejemplo.com",
            telefono="+57 310-123-4567",
            direccion="Calle 123 # 45-67, Soacha"
        )
    except DatoPersonalInvalidoError as e:
        print(f" Error: {e}")
    else:
        print(f" Cliente creado: {cliente1}")
        print(f"   Nombre formateado: {cliente1.nombres_completo}")
        print(f"   Correo normalizado: {cliente1.correo}")
        print(f"   Datos públicos: {cliente1.obtener_datos_publicos()}")

    #  Ejemplo 2: try / except / finally — Correo inválido
    print("\n--- Prueba 2: Correo con formato incorrecto ---")
    cliente2 = None
    try:
        cliente2 = Cliente(
            identificacion="TI-987654",
            nombres="Carlos Andrés",
            apellidos="Ruiz",
            correo="correo_invalido",  # == Sin @ ==
            telefono="3209876543"
        )
    except DatoPersonalInvalidoError as e:
        print(f" No se pudo crear el cliente: {e}")
    finally:
        print(f"   → Resultado final: {'Cliente creado' if cliente2 else 'Creación fallida'}")

    #  Ejemplo 3: raise ... from ... == Encadenamiento de excepciones ==

    print("\n--- Prueba 3: Validación con excepción encadenada ---")
    def registrar_cliente_sistema(datos: dict):
        """Función que simula una capa superior que llama a la creación."""
        try:
            return Cliente(**datos)
        except DatoPersonalInvalidoError as error_original:
            logger.exception("Error en el registro del cliente")
            raise DatoInvalidoError(
                "No se pudo completar el registro. Verifique los datos ingresados."
            ) from error_original

    try:
        registrar_cliente_sistema({
            "identificacion": "",  # Vacío
            "nombres": "Luis",
            "apellidos": "Mora",
            "correo": "luis@correo.com"
        })
    except DatoInvalidoError as e:
        print(f" Mensaje al usuario: {e}")
        print(f" Causa técnica: {e.__cause__}")

    # Intento de acceso directo a atributo privado (no funciona)
    print("\n--- Prueba 4: Protección de datos ---")
    print(" Acceso permitido (vía propiedad):", cliente1.correo)
    try:
        print(" Intento de acceso a __correo:", cliente1.__correo)
    except AttributeError:
        print(" Acceso denegado: los datos privados están protegidos")