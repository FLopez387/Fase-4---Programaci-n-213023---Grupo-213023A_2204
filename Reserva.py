# Clase Reserva
# Programación-213023 — Grupo-213023A_2204
"""
Clase Reserva que integra Cliente, Servicio, duración y estado.
Implementa confirmación, cancelación y procesamiento con manejo
robusto de excepciones (try/except, try/except/else,
try/except/finally, encadenamiento y excepciones personalizadas).
Toda la información se gestiona en memoria y los eventos/errores
se registran en el archivo de logs del sistema.
"""

from datetime import datetime
import logging

# Importaciones del proyecto
from FASE_4 import (
    SoftwareFJError,
    DatoInvalidoError,
    ServicioNoDisponibleError,
)
from servicios import Servicio
from Clase_cliente import Cliente
from calculo_costos import CalculadoraCostos

# Logger del módulo (se escribe en 'sistema_fj.log' configurado en FASE_4)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════
#  EXCEPCIONES PERSONALIZADAS PARA RESERVAS
# ════════════════════════════════════════════════════════════════

class ReservaError(SoftwareFJError):
    """Excepción base para cualquier error relacionado con reservas."""
    pass


class EstadoReservaInvalidoError(ReservaError):
    """Se lanza cuando se intenta una transición de estado no permitida."""
    pass


class DuracionInvalidaError(DatoInvalidoError):
    """Se lanza cuando la duración proporcionada no es válida."""
    pass


class ReservaDuplicadaError(ReservaError):
    """Se lanza cuando ya existe una reserva activa igual."""
    pass


# ════════════════════════════════════════════════════════════════
#  ESTADOS VÁLIDOS Y TRANSICIONES PERMITIDAS
# ════════════════════════════════════════════════════════════════

class EstadoReserva:
    """Constantes de estado y reglas de transición."""
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

    TODOS = {PENDIENTE, CONFIRMADA, EN_PROCESO, COMPLETADA, CANCELADA}

    # estado_actual → conjunto de estados a los que puede pasar
    TRANSICIONES = {
        PENDIENTE:   {CONFIRMADA, CANCELADA},
        CONFIRMADA:  {EN_PROCESO, CANCELADA},
        EN_PROCESO:  {COMPLETADA, CANCELADA},
        COMPLETADA:  set(),   # estado final
        CANCELADA:   set(),   # estado final
    }


# ════════════════════════════════════════════════════════════════
#  CLASE RESERVA
# ════════════════════════════════════════════════════════════════

class Reserva:
    """
    Representa una reserva que asocia un Cliente con un Servicio.

    Atributos encapsulados:
        - cliente   : objeto Cliente
        - servicio  : objeto Servicio (ReservaSala, AlquilerEquipo, etc.)
        - duracion  : duración en horas (int > 0)
        - estado    : estado actual de la reserva
        - fecha_creacion   : marca temporal de creación
        - fecha_confirmacion / fecha_cancelacion / fecha_procesamiento

    Métodos principales:
        confirmar()   → pasa de pendiente a confirmada
        cancelar()    → cancela desde cualquier estado no-final
        procesar()    → pasa de confirmada a en_proceso y luego a completada
    """

    _contador_id = 0  # auto-incremento para generar IDs únicos

    # ----- Constructor -----
    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        impuesto: float = 0,
        descuento: float = 0,
    ):
        # Validar parámetros obligatorios (try/except/else)
        try:
            self._validar_cliente(cliente)
            self._validar_servicio(servicio)
            self._validar_duracion(duracion)
        except (DatoInvalidoError, TypeError) as error:
            logger.error(
                " Error al crear reserva: %s", error, exc_info=True
            )
            raise  # re-lanza la excepción original
        else:
            # Solo se ejecuta si NO hubo excepciones
            Reserva._contador_id += 1
            self.__id_reserva = f"RES-{Reserva._contador_id:04d}"
            self.__cliente = cliente
            self.__servicio = servicio
            self.__duracion = int(duracion)
            self.__estado = EstadoReserva.PENDIENTE
            self.__impuesto = impuesto
            self.__descuento = descuento
            self.__costo_total = None

            # Marcas temporales
            self.__fecha_creacion = datetime.now()
            self.__fecha_confirmacion = None
            self.__fecha_cancelacion = None
            self.__fecha_procesamiento = None
            self.__motivo_cancelacion = ""

            logger.info(
                " Reserva creada: %s | Cliente: %s | Servicio: %s | "
                "Duración: %d h | Estado: %s",
                self.__id_reserva,
                self.__cliente,
                self.__servicio._nombre,
                self.__duracion,
                self.__estado,
            )

    # ══════════════════════════════════════════════════════════
    #  PROPIEDADES (Encapsulación — solo lectura pública)
    # ══════════════════════════════════════════════════════════

    @property
    def id_reserva(self) -> str:
        return self.__id_reserva

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def duracion(self) -> int:
        return self.__duracion

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def costo_total(self):
        return self.__costo_total

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    @property
    def fecha_confirmacion(self):
        return self.__fecha_confirmacion

    @property
    def fecha_cancelacion(self):
        return self.__fecha_cancelacion

    @property
    def fecha_procesamiento(self):
        return self.__fecha_procesamiento

    @property
    def motivo_cancelacion(self) -> str:
        return self.__motivo_cancelacion

    # ══════════════════════════════════════════════════════════
    #  VALIDACIONES INTERNAS
    # ══════════════════════════════════════════════════════════

    @staticmethod
    def _validar_cliente(cliente):
        """Verifica que el objeto cliente sea una instancia válida."""
        if cliente is None:
            raise DatoInvalidoError(
                "El cliente no puede ser nulo. Debe proporcionar un "
                "objeto Cliente válido."
            )
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError(
                f"Se esperaba un objeto Cliente, pero se recibió "
                f"{type(cliente).__name__}."
            )

    @staticmethod
    def _validar_servicio(servicio):
        """Verifica que el objeto servicio sea una instancia válida."""
        if servicio is None:
            raise ServicioNoDisponibleError(
                "El servicio no puede ser nulo. Debe seleccionar un "
                "servicio disponible."
            )
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError(
                f"Se esperaba un objeto Servicio, pero se recibió "
                f"{type(servicio).__name__}."
            )

    @staticmethod
    def _validar_duracion(duracion):
        """
        Verifica que la duración sea un entero positivo.
        Usa encadenamiento de excepciones (raise … from …).
        """
        try:
            valor = int(duracion)
        except (ValueError, TypeError) as error_original:
            raise DuracionInvalidaError(
                f"La duración debe ser un número entero. "
                f"Valor recibido: '{duracion}'."
            ) from error_original

        if valor <= 0:
            raise DuracionInvalidaError(
                f"La duración debe ser mayor a 0 horas. "
                f"Valor recibido: {valor}."
            )
        if valor > 720:  # máximo 30 días
            raise DuracionInvalidaError(
                f"La duración no puede superar las 720 horas (30 días). "
                f"Valor recibido: {valor}."
            )

    def _cambiar_estado(self, nuevo_estado: str):
        """
        Gestiona la transición de estado siguiendo las reglas definidas.
        Lanza EstadoReservaInvalidoError si la transición no es válida.
        """
        estados_posibles = EstadoReserva.TRANSICIONES.get(
            self.__estado, set()
        )
        if nuevo_estado not in estados_posibles:
            raise EstadoReservaInvalidoError(
                f"No se puede pasar de '{self.__estado}' a "
                f"'{nuevo_estado}'. Transiciones permitidas desde "
                f"'{self.__estado}': "
                f"{estados_posibles if estados_posibles else 'ninguna (estado final)'}."
            )
        estado_anterior = self.__estado
        self.__estado = nuevo_estado
        logger.info(
            " Reserva %s: estado cambió de '%s' → '%s'",
            self.__id_reserva, estado_anterior, nuevo_estado,
        )

    # ══════════════════════════════════════════════════════════
    #  MÉTODOS PRINCIPALES: CONFIRMAR, CANCELAR, PROCESAR
    # ══════════════════════════════════════════════════════════

    def confirmar(self) -> bool:
        """
        Confirma la reserva (pendiente → confirmada).
        Calcula el costo total al confirmar.

        Usa: try / except / else / finally
        Retorna True si se confirma exitosamente.
        """
        resultado = False
        try:
            logger.info(
                " Intentando confirmar reserva %s …", self.__id_reserva
            )
            self._cambiar_estado(EstadoReserva.CONFIRMADA)

            # Calcular costo total al confirmar
            calculadora = CalculadoraCostos()
            self.__costo_total = calculadora.calcular_costo_servicio(
                self.__servicio, self.__impuesto, self.__descuento
            )

        except EstadoReservaInvalidoError as e:
            logger.warning(
                " No se pudo confirmar reserva %s: %s",
                self.__id_reserva, e,
            )
            raise
        except DatoInvalidoError as e:
            # Si falla el cálculo del costo, revertir el estado
            self.__estado = EstadoReserva.PENDIENTE
            logger.error(
                " Error en cálculo de costo para reserva %s: %s",
                self.__id_reserva, e,
            )
            raise ReservaError(
                f"No se pudo confirmar la reserva {self.__id_reserva} "
                f"por un error en el cálculo del costo."
            ) from e
        else:
            self.__fecha_confirmacion = datetime.now()
            resultado = True
            logger.info(
                " Reserva %s confirmada. Costo total: $%s",
                self.__id_reserva, self.__costo_total,
            )
        finally:
            logger.info(
                " Fin del proceso de confirmación para reserva %s. "
                "Estado actual: %s",
                self.__id_reserva, self.__estado,
            )

        return resultado

    def cancelar(self, motivo: str = "No especificado") -> bool:
        """
        Cancela la reserva desde cualquier estado no-final.

        Usa: try / except / finally
        Retorna True si se cancela exitosamente.
        """
        resultado = False
        try:
            logger.info(
                " Intentando cancelar reserva %s. Motivo: %s",
                self.__id_reserva, motivo,
            )

            if not isinstance(motivo, str) or not motivo.strip():
                raise DatoInvalidoError(
                    "Debe proporcionar un motivo de cancelación válido."
                )

            self._cambiar_estado(EstadoReserva.CANCELADA)
            self.__motivo_cancelacion = motivo.strip()
            self.__fecha_cancelacion = datetime.now()
            resultado = True

            logger.info(
                " Reserva %s cancelada exitosamente. Motivo: '%s'",
                self.__id_reserva, self.__motivo_cancelacion,
            )

        except EstadoReservaInvalidoError as e:
            logger.warning(
                " No se pudo cancelar reserva %s: %s",
                self.__id_reserva, e,
            )
            raise
        except DatoInvalidoError as e:
            logger.error(
                " Dato inválido al cancelar reserva %s: %s",
                self.__id_reserva, e,
            )
            raise
        finally:
            logger.info(
                " Fin del proceso de cancelación para reserva %s. "
                "Estado actual: %s",
                self.__id_reserva, self.__estado,
            )

        return resultado

    def procesar(self) -> bool:
        """
        Procesa la reserva completa:
            confirmada → en_proceso → completada

        Usa: try / except / else / finally  +  encadenamiento
        Retorna True si el procesamiento se completa exitosamente.
        """
        resultado = False
        try:
            logger.info(
                " Iniciando procesamiento de reserva %s …",
                self.__id_reserva,
            )

            # Paso 1: pasar a 'en_proceso'
            self._cambiar_estado(EstadoReserva.EN_PROCESO)

            # Paso 2: simulación de lógica de negocio
            if self.__costo_total is None:
                raise ReservaError(
                    f"La reserva {self.__id_reserva} no tiene costo "
                    f"calculado. Debe confirmarla antes de procesarla."
                )

            # Paso 3: completar la reserva
            self._cambiar_estado(EstadoReserva.COMPLETADA)

        except EstadoReservaInvalidoError as e:
            logger.warning(
                " Transición inválida al procesar reserva %s: %s",
                self.__id_reserva, e,
            )
            raise
        except ReservaError as e:
            logger.error(
                " Error de negocio al procesar reserva %s: %s",
                self.__id_reserva, e,
            )
            raise
        except Exception as e:
            # Captura cualquier error inesperado
            logger.critical(
                " Error inesperado al procesar reserva %s: %s",
                self.__id_reserva, e, exc_info=True,
            )
            raise ReservaError(
                f"Error inesperado al procesar la reserva "
                f"{self.__id_reserva}."
            ) from e
        else:
            self.__fecha_procesamiento = datetime.now()
            resultado = True
            logger.info(
                " Reserva %s procesada y completada exitosamente.",
                self.__id_reserva,
            )
        finally:
            logger.info(
                " Fin del procesamiento para reserva %s. "
                "Estado actual: %s",
                self.__id_reserva, self.__estado,
            )

        return resultado

    # ══════════════════════════════════════════════════════════
    #  MÉTODOS DE REPRESENTACIÓN
    # ══════════════════════════════════════════════════════════

    def obtener_resumen(self) -> dict:
        """Devuelve un diccionario con el resumen de la reserva."""
        return {
            "id_reserva": self.__id_reserva,
            "cliente": self.__cliente.nombres_completo,
            "cliente_id": self.__cliente.identificacion,
            "servicio": self.__servicio._nombre,
            "servicio_id": self.__servicio.id_servicio,
            "duracion_horas": self.__duracion,
            "estado": self.__estado,
            "costo_total": str(self.__costo_total) if self.__costo_total else "Sin calcular",
            "fecha_creacion": self.__fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_confirmacion": (
                self.__fecha_confirmacion.strftime("%Y-%m-%d %H:%M:%S")
                if self.__fecha_confirmacion else "—"
            ),
            "fecha_cancelacion": (
                self.__fecha_cancelacion.strftime("%Y-%m-%d %H:%M:%S")
                if self.__fecha_cancelacion else "—"
            ),
            "fecha_procesamiento": (
                self.__fecha_procesamiento.strftime("%Y-%m-%d %H:%M:%S")
                if self.__fecha_procesamiento else "—"
            ),
            "motivo_cancelacion": self.__motivo_cancelacion or "—",
        }

    def __str__(self) -> str:
        return (
            f"Reserva({self.__id_reserva} | "
            f"Cliente: {self.__cliente.nombres_completo} | "
            f"Servicio: {self.__servicio._nombre} | "
            f"Duración: {self.__duracion}h | "
            f"Estado: {self.__estado})"
        )

    def __repr__(self) -> str:
        return f"<Reserva: {self.__id_reserva} [{self.__estado}]>"


# ════════════════════════════════════════════════════════════════
#  EJEMPLOS DE USO CON MANEJO DE EXCEPCIONES
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from servicios import ReservaSala, AlquilerEquipo

    print("=" * 65)
    print("  SISTEMA DE RESERVAS — Software FJ")
    print("=" * 65)

    # ── Crear objetos de prueba ──
    cliente_prueba = None
    servicio_prueba = None

    # try / except / else  → creación del cliente
    print("\n--- Paso 1: Crear cliente de prueba ---")
    try:
        cliente_prueba = Cliente(
            identificacion="CC-1234567890",
            nombres="Ana María",
            apellidos="López Rodríguez",
            correo="ana.lopez@correo.com",
            telefono="+57 300-111-2233",
        )
    except DatoInvalidoError as e:
        print(f"   No se pudo crear el cliente: {e}")
    else:
        print(f"   {cliente_prueba}")

    # try / except / else → creación del servicio
    print("\n--- Paso 2: Crear servicio de prueba ---")
    try:
        servicio_prueba = ReservaSala(
            id_servicio="SALA-001",
            nombre="Sala de Conferencias A",
            costo_base=150000,
            capacidad=20,
        )
    except Exception as e:
        print(f"   No se pudo crear el servicio: {e}")
    else:
        print(f"   Servicio: {servicio_prueba._nombre} "
              f"(costo base: ${servicio_prueba._costo_base:,.0f})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PRUEBA 1: Flujo completo exitoso
    #   crear → confirmar → procesar
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "─" * 65)
    print(" PRUEBA 1: Flujo completo (crear → confirmar → procesar)")
    print("─" * 65)

    reserva1 = None
    try:
        reserva1 = Reserva(
            cliente=cliente_prueba,
            servicio=servicio_prueba,
            duracion=3,
            impuesto=19,
            descuento=5,
        )
        print(f"   {reserva1}")
    except (DatoInvalidoError, ServicioNoDisponibleError) as e:
        print(f"   Error al crear reserva: {e}")

    if reserva1:
        # Confirmar
        try:
            reserva1.confirmar()
            print(f"   Reserva confirmada. Costo: ${reserva1.costo_total}")
        except (EstadoReservaInvalidoError, ReservaError) as e:
            print(f"   Error al confirmar: {e}")

        # Procesar
        try:
            reserva1.procesar()
            print(f"   Reserva procesada. Estado final: {reserva1.estado}")
        except (EstadoReservaInvalidoError, ReservaError) as e:
            print(f"   Error al procesar: {e}")

        # Mostrar resumen
        print("\n   Resumen de la reserva:")
        for clave, valor in reserva1.obtener_resumen().items():
            print(f"     {clave:>22}: {valor}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PRUEBA 2: Cancelación de reserva
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "─" * 65)
    print(" PRUEBA 2: Cancelación de reserva")
    print("─" * 65)

    reserva2 = None
    try:
        servicio2 = AlquilerEquipo(
            id_servicio="EQP-002",
            nombre="Proyector 4K",
            costo_base=50000,
            horas=4,
        )
        reserva2 = Reserva(
            cliente=cliente_prueba,
            servicio=servicio2,
            duracion=4,
        )
        print(f"   {reserva2}")
        reserva2.cancelar(motivo="El cliente reprogramó la reunión")
        print(f"   Reserva cancelada. Estado: {reserva2.estado}")
    except ReservaError as e:
        print(f"  Error: {e}")

    # Intentar cancelar de nuevo (debe fallar: estado final)
    if reserva2:
        try:
            reserva2.cancelar(motivo="Segundo intento")
        except EstadoReservaInvalidoError as e:
            print(f"   Esperado — No se puede cancelar de nuevo: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PRUEBA 3: Errores de validación
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "─" * 65)
    print(" PRUEBA 3: Errores de validación al crear reservas")
    print("─" * 65)

    # 3a — Cliente nulo
    print("\n  3a) Cliente nulo:")
    try:
        Reserva(cliente=None, servicio=servicio_prueba, duracion=2)
    except DatoInvalidoError as e:
        print(f"      {e}")

    # 3b — Servicio nulo
    print("\n  3b) Servicio nulo:")
    try:
        Reserva(cliente=cliente_prueba, servicio=None, duracion=2)
    except ServicioNoDisponibleError as e:
        print(f"      {e}")

    # 3c — Duración inválida (negativa)
    print("\n  3c) Duración negativa:")
    try:
        Reserva(cliente=cliente_prueba, servicio=servicio_prueba, duracion=-5)
    except DuracionInvalidaError as e:
        print(f"      {e}")

    # 3d — Duración inválida (texto) — encadenamiento
    print("\n  3d) Duración con texto (encadenamiento de excepciones):")
    try:
        Reserva(
            cliente=cliente_prueba,
            servicio=servicio_prueba,
            duracion="abc",
        )
    except DuracionInvalidaError as e:
        print(f"     Duraacion Invalida {e}")
        print(f"     Causa original: {e.__cause__}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PRUEBA 4: Intentar procesar sin confirmar
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "─" * 65)
    print(" PRUEBA 4: Procesar reserva sin confirmar primero")
    print("─" * 65)

    try:
        reserva4 = Reserva(
            cliente=cliente_prueba,
            servicio=servicio_prueba,
            duracion=1,
        )
        reserva4.procesar()  # Debe fallar: pendiente → en_proceso no permitido
    except EstadoReservaInvalidoError as e:
        print(f"   Esperado — {e}")
    except ReservaError as e:
        print(f"  Error {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PRUEBA 5: Confirmar una reserva ya completada
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "─" * 65)
    print(" PRUEBA 5: Confirmar reserva ya completada")
    print("─" * 65)

    if reserva1:
        try:
            reserva1.confirmar()
        except EstadoReservaInvalidoError as e:
            print(f"   Esperado — {e}")

    print("\n" + "=" * 65)
    print("Todas las pruebas de la clase Reserva finalizaron.")
    print("=" * 65)
