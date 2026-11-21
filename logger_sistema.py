import logging
from pathlib import Path


def configurar_logger(nombre_archivo: str = "software_fj.log") -> logging.Logger:
    """Configura un logger que guarda eventos y errores en archivo de texto plano."""
    ruta_log = Path(__file__).resolve().parent / nombre_archivo
    logger = logging.getLogger("SoftwareFJLogger")
    logger.setLevel(logging.INFO)

    # Evita duplicar handlers si se importa el módulo varias veces
    if not logger.handlers:
        file_handler = logging.FileHandler(ruta_log, mode="a", encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger