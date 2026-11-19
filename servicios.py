# Servicios de Software FJ 
# Programacion-213023---Grupo-213023A_2204
"""
Clase abstracta Servicio y tres servicios especializados:
ReservaSala, AlquilerEquipo y AsesoriaEspecializada.

Aplica abstracción, herencia, polimorfismo (métodos sobrescritos),
encapsulación y manejo de excepciones personalizadas con encadenamiento.
Es compatible con FASE_4.py (excepciones), calculo_costos.py
(calcular_costo() sin parámetros) y con la futura clase Reserva.

Jairo Martin Corrales Navarro
"""
import logging
from abc import ABC, abstractmethod

# Excepciones base definidas por el equipo en FASE_4.py
from FASE_4 import DatoInvalidoError, ServicioNoDisponibleError

# Logger del módulo (la configuración del archivo de logs la hace FASE_4.py)
logger = logging.getLogger(__name__)


# ===== 1. EXCEPCIONES ESPECÍFICAS DE SERVICIOS =====

class ParametroServicioInvalidoError(DatoInvalidoError):
    """Se lanza cuando un parámetro de un servicio no es válido."""
    codigo_error = "ERR-SRV-001"


# ===== 2. CLASE ABSTRACTA SERVICIO =====

class Servicio(ABC):
    """
    Clase abstracta que representa un servicio general de Software FJ.
    Define el contrato que todo servicio especializado debe cumplir.
    """

    def __init__(self, id_servicio: str, nombre: str, costo_base: float):
        # Atributos protegidos (encapsulación): se exponen vía propiedades
        self._id_servicio = id_servicio
        self._nombre = nombre
        self._costo_base = costo_base
        # Indica si el servicio puede ser reservado actualmente
        self._disponible = True

    # ----- Propiedades de solo lectura -----

    @property
    def id_servicio(self) -> str:
        """Identificador único del servicio."""
        return self._id_servicio

    @property
    def nombre(self) -> str:
        """Nombre comercial del servicio."""
        return self._nombre

    @property
    def costo_base(self) -> float:
        """Tarifa base del servicio (por hora)."""
        return self._costo_base

    @property
    def disponible(self) -> bool:
        """True si el servicio se puede reservar."""
        return self._disponible

    # ----- Métodos concretos compartidos por todos los servicios -----

    def marcar_disponible(self, estado: bool) -> None:
        """Cambia la disponibilidad del servicio y deja registro en el log."""
        self._disponible = bool(estado)
        logger.info("Servicio %s disponible=%s", self._id_servicio, self._disponible)

    def verificar_disponibilidad(self) -> None:
        """Lanza ServicioNoDisponibleError si el servicio no se puede reservar."""
        if not self._disponible:
            logger.warning("Servicio no disponible: %s", self._id_servicio)
            raise ServicioNoDisponibleError(
                f"El servicio '{self._nombre}' no está disponible en este momento."
            )

    # ----- Métodos abstractos (deben sobrescribirse en las clases hijas) -----

    @abstractmethod
    def calcular_costo(self) -> float:
        """Calcula el costo total del servicio (polimorfismo)."""

    @abstractmethod
    def describir_servicio(self) -> str:
        """Devuelve una descripción legible del servicio (polimorfismo)."""

    @abstractmethod
    def validar_parametros(self) -> None:
        """
        Valida los parámetros comunes. Las clases hijas la sobrescriben,
        llaman a super().validar_parametros() y agregan sus propias reglas.
        """
        # Validación del identificador: texto no vacío
        if not isinstance(self._id_servicio, str) or not self._id_servicio.strip():
            raise ParametroServicioInvalidoError("El id del servicio no puede estar vacío.")
        # Validación del nombre: texto no vacío
        if not isinstance(self._nombre, str) or not self._nombre.strip():
            raise ParametroServicioInvalidoError("El nombre del servicio no puede estar vacío.")
        # Validación del costo base: número (no booleano) mayor que cero
        if (
            isinstance(self._costo_base, bool)
            or not isinstance(self._costo_base, (int, float))
            or self._costo_base <= 0
        ):
            raise ParametroServicioInvalidoError("El costo base debe ser un número mayor que cero.")

    # ----- Métodos especiales -----

    def __str__(self) -> str:
        return self.describir_servicio()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self._id_servicio}>"


# ===== 3. SERVICIOS ESPECIALIZADOS =====

class ReservaSala(Servicio):
    """Reserva de una sala de reuniones. Incluye recargo por mantenimiento."""

    RECARGO_MANTENIMIENTO = 0.15  # 15 % sobre el valor de las horas

    def __init__(self, id_servicio: str, nombre: str, costo_base: float,
                 capacidad: int, horas: int = 1):
        super().__init__(id_servicio, nombre, costo_base)
        self._capacidad = capacidad
        self._horas = horas
        # Se validan los datos al crear el objeto (falla rápido)
        self.validar_parametros()

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def horas(self) -> int:
        return self._horas

    def validar_parametros(self) -> None:
        super().validar_parametros()  # reglas comunes
        if isinstance(self._capacidad, bool) or not isinstance(self._capacidad, int) \
                or not 1 <= self._capacidad <= 200:
            raise ParametroServicioInvalidoError("La capacidad de la sala debe ser un entero entre 1 y 200.")
        if isinstance(self._horas, bool) or not isinstance(self._horas, int) \
                or not 1 <= self._horas <= 12:
            raise ParametroServicioInvalidoError("Las horas de la sala deben ser un entero entre 1 y 12.")

    def calcular_costo(self) -> float:
        # Costo = tarifa por hora * horas + recargo de mantenimiento
        subtotal = self._costo_base * self._horas
        return round(subtotal * (1 + self.RECARGO_MANTENIMIENTO), 2)

    def describir_servicio(self) -> str:
        return (f"Reserva de sala '{self._nombre}' ({self._id_servicio}) - "
                f"capacidad {self._capacidad} personas, {self._horas} h")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos por horas. Descuento por alquileres largos."""

    HORAS_PARA_DESCUENTO = 8   # desde 8 horas aplica descuento
    DESCUENTO_LARGO = 0.10     # 10 %

    def __init__(self, id_servicio: str, nombre: str, costo_base: float,
                 horas: int, cantidad: int = 1):
        super().__init__(id_servicio, nombre, costo_base)
        self._horas = horas
        self._cantidad = cantidad
        self.validar_parametros()

    @property
    def horas(self) -> int:
        return self._horas

    @property
    def cantidad(self) -> int:
        return self._cantidad

    def validar_parametros(self) -> None:
        super().validar_parametros()
        if isinstance(self._horas, bool) or not isinstance(self._horas, int) \
                or not 1 <= self._horas <= 72:
            raise ParametroServicioInvalidoError("Las horas de alquiler deben ser un entero entre 1 y 72.")
        if isinstance(self._cantidad, bool) or not isinstance(self._cantidad, int) \
                or not 1 <= self._cantidad <= 50:
            raise ParametroServicioInvalidoError("La cantidad de equipos debe ser un entero entre 1 y 50.")

    def calcular_costo(self) -> float:
        # Costo = tarifa por hora * horas * cantidad de equipos
        total = self._costo_base * self._horas * self._cantidad
        if self._horas >= self.HORAS_PARA_DESCUENTO:
            total *= (1 - self.DESCUENTO_LARGO)
        return round(total, 2)

    def describir_servicio(self) -> str:
        return (f"Alquiler de equipo '{self._nombre}' ({self._id_servicio}) - "
                f"{self._cantidad} unidad(es) por {self._horas} h")


class AsesoriaEspecializada(Servicio):
    """Asesoría con un especialista. La tarifa depende del nivel."""

    # Multiplicador de tarifa según el nivel del asesor
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, id_servicio: str, nombre: str, costo_base: float,
                 especialidad: str, horas: int, nivel: str = "junior"):
        super().__init__(id_servicio, nombre, costo_base)
        self._especialidad = especialidad
        self._horas = horas
        # Se normaliza el nivel solo si es texto; si no, validar_parametros lo rechaza
        self._nivel = nivel.strip().lower() if isinstance(nivel, str) else nivel
        self.validar_parametros()

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @property
    def horas(self) -> int:
        return self._horas

    @property
    def nivel(self) -> str:
        return self._nivel

    def validar_parametros(self) -> None:
        super().validar_parametros()
        if not isinstance(self._especialidad, str) or not self._especialidad.strip():
            raise ParametroServicioInvalidoError("La especialidad de la asesoría no puede estar vacía.")
        if isinstance(self._horas, bool) or not isinstance(self._horas, int) \
                or not 1 <= self._horas <= 8:
            raise ParametroServicioInvalidoError("Las horas de asesoría deben ser un entero entre 1 y 8.")
        if self._nivel not in self.NIVELES:
            raise ParametroServicioInvalidoError(
                f"Nivel inválido. Opciones: {', '.join(self.NIVELES)}."
            )

    def calcular_costo(self) -> float:
        # Costo = tarifa por hora * horas * multiplicador del nivel
        return round(self._costo_base * self._horas * self.NIVELES[self._nivel], 2)

    def describir_servicio(self) -> str:
        return (f"Asesoría de {self._especialidad} '{self._nombre}' ({self._id_servicio}) - "
                f"nivel {self._nivel}, {self._horas} h")


# ===== 4. FÁBRICA CON ENCADENAMIENTO DE EXCEPCIONES =====

def crear_servicio(tipo: str, **datos) -> Servicio:
    """
    Crea un servicio según su tipo ('sala', 'equipo' o 'asesoria').
    Convierte errores de bajo nivel en DatoInvalidoError usando 'raise ... from'.
    """
    tipos = {"sala": ReservaSala, "equipo": AlquilerEquipo, "asesoria": AsesoriaEspecializada}
    try:
        return tipos[tipo](**datos)
    except KeyError as error:
        logger.error("Tipo de servicio desconocido: %s", tipo)
        raise DatoInvalidoError(f"Tipo de servicio desconocido: '{tipo}'.") from error
    except TypeError as error:  # parámetros faltantes o sobrantes
        logger.error("Parámetros incorrectos para '%s': %s", tipo, error)
        raise DatoInvalidoError("Faltan parámetros o hay parámetros no permitidos.") from error
    except ParametroServicioInvalidoError as error:
        logger.error("Servicio '%s' inválido: %s", tipo, error)
        raise  # ya es una excepción propia; se relanza tal cual


# ===== 5. DEMOSTRACIÓN =====

if __name__ == "__main__":
    print("=" * 60)
    print("GESTIÓN DE SERVICIOS - SOFTWARE FJ")
    print("=" * 60)

    # Prueba 1: creación válida y polimorfismo
    print("\n--- Prueba 1: servicios válidos (polimorfismo) ---")
    servicios = [
        crear_servicio("sala", id_servicio="SAL-01", nombre="Sala Ejecutiva",
                       costo_base=50000, capacidad=12, horas=3),
        crear_servicio("equipo", id_servicio="EQ-01", nombre="Portátil",
                       costo_base=8000, horas=10, cantidad=2),
        crear_servicio("asesoria", id_servicio="ASE-01", nombre="Revisión de código",
                       costo_base=60000, especialidad="Python", horas=2, nivel="Senior"),
    ]
    for s in servicios:  # mismo método, comportamiento distinto en cada clase
        print(f"  {s.describir_servicio()} -> ${s.calcular_costo():,.2f}")

    # Prueba 2: datos inválidos (try / except / else / finally)
    print("\n--- Prueba 2: parámetros inválidos ---")
    casos_invalidos = [
        ("sala", dict(id_servicio="SAL-02", nombre="Sala X", costo_base=-10, capacidad=5)),
        ("equipo", dict(id_servicio="EQ-02", nombre="Proyector", costo_base=5000, horas=0)),
        ("asesoria", dict(id_servicio="ASE-02", nombre="Asesoría", costo_base=40000,
                          especialidad="SQL", horas=2, nivel="gurú")),
        ("sala", dict(id_servicio="SAL-03", nombre="Sala Y")),  # faltan parámetros
        ("hotel", dict()),                                       # tipo inexistente
    ]
    for tipo, datos in casos_invalidos:
        creado = None
        try:
            creado = crear_servicio(tipo, **datos)
        except DatoInvalidoError as e:
            print(f"  [ERROR] {tipo}: {e}")
            if e.__cause__:
                print(f"          causa: {type(e.__cause__).__name__}")
        else:
            print(f"  [OK] {creado}")
        finally:
            print(f"          resultado: {'creado' if creado else 'rechazado'}")

    # Prueba 3: servicio no disponible
    print("\n--- Prueba 3: servicio no disponible ---")
    servicios[0].marcar_disponible(False)
    try:
        servicios[0].verificar_disponibilidad()
    except ServicioNoDisponibleError as e:
        print(f"  [ERROR] {e}")

    # Prueba 4: la clase abstracta no se puede instanciar
    print("\n--- Prueba 4: clase abstracta ---")
    try:
        Servicio("X", "X", 1)
    except TypeError as e:
        print(f"  [ERROR] No se puede instanciar Servicio: {e}")
