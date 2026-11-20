# config_logging.py
# Módulo auxiliar de configuración de logging para el sistema Software FJ
import logging


def configurar_logging():
    """Configura el sistema de logging para escribir en archivo y consola."""
    logging.basicConfig(
        filename='sistema_fj.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
