import logging
import sys
import runpy


# Excepciones personalizadas del sistema
class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ."""
    pass


class DatoInvalidoError(SoftwareFJError):
    """Error cuando un dato ingresado no es válido."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Error cuando un servicio no está disponible."""
    pass


# Configuración del registro de eventos
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SoftwareFJ")


def ejecutar_sistema():
    logger.info("Iniciando el sistema integrado Software FJ.")

    # Evita que Reserva.py importe una segunda copia de FASE_4
    sys.modules.setdefault("FASE_4", sys.modules[__name__])

    # Ejecuta el flujo principal existente de Reserva.py
    runpy.run_module("Reserva", run_name="__main__")


def main():
    try:
        ejecutar_sistema()
    except Exception as error:
        logger.exception("Error durante la ejecución del sistema.")
        print(f"\n[ERROR] {error}")
    finally:
        logger.info("Finalizó la ejecución del sistema.")


if __name__ == "__main__":
    main()