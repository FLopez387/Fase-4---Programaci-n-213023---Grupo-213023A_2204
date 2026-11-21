# Fase-4---Programacion-213023---Grupo-213023A_2204

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import sys
import runpy

# Configuración del sistema de logs
logging.basicConfig(
    filename='sistema_fj.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- 1. EXCEPCIONES PERSONALIZADAS ---
class SoftwareFJError(Exception):
    """Excepción base para el sistema de Software FJ."""
    pass


class DatoInvalidoError(SoftwareFJError):
    """Se lanza cuando un parámetro o dato ingresado no es válido."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un servicio no está disponible o la reserva falla."""
    pass


# --- 2. CLASE ABSTRACTA ---
class Servicio(ABC):
    def __init__(self, id_servicio: str, nombre: str, costo_base: float):
        self._id_servicio = id_servicio
        self._nombre = nombre
        self._costo_base = costo_base

    @property
    def id_servicio(self):
        return self._id_servicio

    @abstractmethod
    def calcular_costo(self) -> float:
        """Método abstracto que implementarán las clases hijas."""
        pass


# --- 3. CLASES DERIVADAS ---
class ReservaSala(Servicio):
    def __init__(self, id_servicio: str, nombre: str,
                 costo_base: float, capacidad: int):
        super().__init__(id_servicio, nombre, costo_base)
        self.capacidad = capacidad

    def calcular_costo(self) -> float:
        return self._costo_base * 1.15


class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio: str, nombre: str,
                 costo_base: float, horas: int):
        super().__init__(id_servicio, nombre, costo_base)
        self.horas = horas

    def calcular_costo(self) -> float:
        return self._costo_base * self.horas


# --- 4. PROCESAMIENTO CON TRY / EXCEPT / ELSE / FINALLY ---
def procesar_reserva(servicio: Servicio):
    try:
        logging.info(
            f"Iniciando procesamiento para el servicio: "
            f"{servicio.id_servicio}"
        )

        if servicio._costo_base <= 0:
            raise DatoInvalidoError(
                "El costo base no puede ser negativo o cero."
            )

        costo_total = servicio.calcular_costo()

    except DatoInvalidoError as e:
        logging.error(f"Error de validación: {e}")
        print(f"[ALERTA] Dato inválido detectado: {e}")

    except Exception as e:
        logging.critical(f"Error inesperado: {e}")
        print(f"[CRÍTICO] Ocurrió un error inesperado: {e}")

    else:
        logging.info(
            f"Reserva procesada con éxito. Costo total: {costo_total}"
        )
        print(
            f"[ÉXITO] Servicio procesado correctamente. "
            f"Total a pagar: ${costo_total:.2f}"
        )

    finally:
        logging.info(
            "Finalizó el intento de transacción de reserva.\n"
        )


# --- 5. INTEGRACIÓN DEL SISTEMA SOFTWARE FJ ---
def ejecutar_sistema():
    logging.info("Iniciando sistema integrado Software FJ.")

    # Permite que Reserva.py reutilice las excepciones de este módulo.
    sys.modules.setdefault("FASE_4", sys.modules[__name__])

    # Ejecuta el flujo integrado de reservas.
    runpy.run_module("Reserva", run_name="__main__")


def main():
    try:
        ejecutar_sistema()

    except Exception as error:
        logging.exception("Error durante la ejecución del sistema.")
        print(f"\n[ERROR] {error}")

    finally:
        logging.info("Finalizó la ejecución del sistema.")


if __name__ == "__main__":
    main()