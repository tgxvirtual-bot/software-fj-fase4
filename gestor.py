from excepciones import ErrorSoftwareFJ
from logger_sistema import configurar_logger
from modelos import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    Reserva,
    ReservaSala,
    Servicio,
)


class GestorSoftwareFJ:
    """Gestiona clientes, servicios y reservas en memoria (listas) con logs en archivo."""

    def __init__(self, archivo_log: str = "software_fj.log"):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        self.logger = configurar_logger(archivo_log)

    def ejecutar_operacion(self, descripcion: str, accion):
        """
        Ejecuta una operación aplicando try / except / else / finally
        y registrando resultados o excepciones en el archivo .log sin detener el programa.
        """
        resultado = None
        exito = False
        print(f"\n--- Operación: {descripcion} ---")
        try:
            resultado = accion()
        except ErrorSoftwareFJ as err:
            self.logger.error(
                f"[{err.codigo}] {descripcion} -> {err} (timestamp={err.timestamp})"
            )
            print(f"[ERROR CONTROLADO - {err.codigo}]: {err}")
        except Exception as err:
            self.logger.critical(f"[ERROR_INESPERADO] {descripcion} -> {type(err).__name__}: {err}")
            print(f"[ERROR INESPERADO]: {err}")
        else:
            exito = True
            self.logger.info(f"[OK] {descripcion}")
            print("[ÉXITO] Operación completada correctamente.")
        finally:
            estado_cierre = "EXITOSA" if exito else "FALLIDA"
            self.logger.info(f"[CIERRE_OPERACION] '{descripcion}' finalizó con estado {estado_cierre}.")
        return resultado

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        if any(c.id == cliente.id for c in self.clientes):
            from excepciones import DatoInvalidoError
            raise DatoInvalidoError(f"Ya existe un cliente registrado con ID '{cliente.id}'.")
        self.clientes.append(cliente)
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if any(s.id == servicio.id for s in self.servicios):
            from excepciones import DatoInvalidoError
            raise DatoInvalidoError(f"Ya existe un servicio registrado con ID '{servicio.id}'.")
        self.servicios.append(servicio)
        return servicio

    def crear_reserva(self, reserva: Reserva) -> Reserva:
        if any(r.id == reserva.id for r in self.reservas):
            from excepciones import OperacionReservaError
            raise OperacionReservaError(f"Ya existe una reserva con ID '{reserva.id}'.")
        self.reservas.append(reserva)
        return reserva

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        for c in self.clientes:
            if c.id == id_cliente.upper():
                return c
        from excepciones import DisponibilidadError
        raise DisponibilidadError(f"No se encontró cliente con ID '{id_cliente}'.")

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        for s in self.servicios:
            if s.id == id_servicio.upper():
                return s
        from excepciones import DisponibilidadError
        raise DisponibilidadError(f"No se encontró servicio con ID '{id_servicio}'.")

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        for r in self.reservas:
            if r.id == id_reserva.upper():
                return r
        from excepciones import OperacionReservaError
        raise OperacionReservaError(f"No se encontró reserva con ID '{id_reserva}'.")