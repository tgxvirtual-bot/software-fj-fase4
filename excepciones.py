from datetime import datetime


class ErrorSoftwareFJ(Exception):
    """Excepción base del sistema Software FJ con código y marca de tiempo."""

    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        super().__init__(mensaje)
        self.codigo = codigo
        self.timestamp = datetime.now().isoformat()


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un dato de entrada es inválido, vacío o está fuera de rango."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR_DATO_INVALIDO")


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se lanza cuando falta un parámetro obligatorio o requerido para la operación."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR_PARAMETRO_FALTANTE")


class DisponibilidadError(ErrorSoftwareFJ):
    """Se lanza cuando un cliente o servicio no está disponible para operar."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR_DISPONIBILIDAD")


class OperacionReservaError(ErrorSoftwareFJ):
    """Se lanza cuando ocurre una operación no permitida en una reserva."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR_OPERACION_RESERVA")


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando un cálculo financiero o numérico produce resultados inválidos."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR_CALCULO_INCONSISTENTE")