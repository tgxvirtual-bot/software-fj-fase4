from abc import ABC, abstractmethod
from functools import singledispatchmethod
import re

from excepciones import (
    CalculoInconsistenteError,
    DatoInvalidoError,
    DisponibilidadError,
    OperacionReservaError,
    ParametroFaltanteError,
)


class EntidadSistema(ABC):
    """Clase abstracta general para entidades identificables dentro de Software FJ."""

    def __init__(self, id_entidad: str):
        if id_entidad is None:
            raise ParametroFaltanteError("El identificador (id) es obligatorio.")
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise DatoInvalidoError("El identificador (id) debe ser un texto no vacío.")
        self._id = id_entidad.strip().upper()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def resumen(self) -> str:
        """Retorna un resumen legible de la entidad."""
        pass


class Cliente(EntidadSistema):
    """Representa un cliente con datos personales encapsulados y validaciones estrictas."""

    def __init__(
        self,
        id_cliente: str,
        nombre: str,
        correo: str,
        telefono: str,
        activo: bool = True,
    ):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self._activo = bool(activo)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if valor is None:
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if valor is None:
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not isinstance(valor, str) or not re.match(patron, valor.strip()):
            raise DatoInvalidoError(f"Correo electrónico no válido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if valor is None:
            raise ParametroFaltanteError("El teléfono del cliente es obligatorio.")
        limpio = re.sub(r"[\s\-\(\)]", "", str(valor))
        if not limpio.isdigit() or len(limpio) < 7:
            raise DatoInvalidoError(f"Número de teléfono inválido: '{valor}'.")
        self._telefono = limpio

    @property
    def activo(self) -> bool:
        return self._activo

    def activar(self) -> None:
        self._activo = True

    def desactivar(self) -> None:
        self._activo = False

    def resumen(self) -> str:
        estado = "ACTIVO" if self._activo else "INACTIVO"
        return (
            f"Cliente[{self._id}] {self._nombre} | Correo: {self._correo} | "
            f"Tel: {self._telefono} | Estado: {estado}"
        )


class Servicio(EntidadSistema):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ):
        super().__init__(id_servicio)
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if valor is None:
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del servicio debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor):
        if valor is None:
            raise ParametroFaltanteError("La tarifa base del servicio es obligatoria.")
        try:
            monto = float(valor)
        except (ValueError, TypeError) as exc:
            raise DatoInvalidoError(
                f"La tarifa base '{valor}' no es un valor numérico válido."
            ) from exc

        if monto <= 0:
            raise DatoInvalidoError("La tarifa base debe ser mayor que cero.")
        self._tarifa_base = monto

    @property
    def disponible(self) -> bool:
        return self._disponible

    def establecer_disponibilidad(self, estado: bool) -> None:
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, cantidad: int) -> int:
        """Valida y normaliza la cantidad/duración requerida por el servicio."""
        pass

    @abstractmethod
    def calcular_costo(
        self,
        cantidad: int,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        recargo_adicional: float = 0.0,
    ) -> float:
        """
        Método sobrecargado vía parámetros opcionales:
        permite calcular costo con solo cantidad o agregando descuento, impuesto y recargo.
        """
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Describe los detalles propios de cada tipo de servicio."""
        pass

    def _aplicar_reglas_financieras(
        self,
        subtotal: float,
        descuento: float,
        impuesto: float,
        recargo_adicional: float,
    ) -> float:
        try:
            desc = float(descuento)
            imp = float(impuesto)
            rec = float(recargo_adicional)
        except (ValueError, TypeError) as exc:
            raise CalculoInconsistenteError(
                "Los parámetros financieros (descuento, impuesto, recargo) deben ser numéricos."
            ) from exc

        if not (0.0 <= desc < 1.0):
            raise DatoInvalidoError("El descuento debe estar entre 0.0 y 0.99.")
        if imp < 0.0 or imp > 1.0:
            raise DatoInvalidoError("El impuesto debe estar entre 0.0 y 1.0.")
        if rec < 0.0:
            raise DatoInvalidoError("El recargo adicional no puede ser negativo.")

        con_recargo = subtotal + rec
        con_descuento = con_recargo * (1.0 - desc)
        total = round(con_descuento * (1.0 + imp), 2)

        if total <= 0:
            raise CalculoInconsistenteError("El total calculado no puede ser menor o igual a cero.")
        return total

    def resumen(self) -> str:
        estado = "DISPONIBLE" if self._disponible else "NO DISPONIBLE"
        return (
            f"Servicio[{self._id}] {self._nombre} | Tarifa base: ${self._tarifa_base:,.2f} | "
            f"{estado}"
        )


class ReservaSala(Servicio):
    """Servicio para reserva de salas de reuniones o capacitación (por horas)."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        capacidad: int,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if capacidad is None:
            raise ParametroFaltanteError("La capacidad de la sala es obligatoria.")
        try:
            cap = int(capacidad)
        except (ValueError, TypeError) as exc:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero.") from exc
        if cap < 2:
            raise DatoInvalidoError("Una sala debe tener capacidad mínima de 2 personas.")
        self._capacidad = cap

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def validar_parametros(self, cantidad: int) -> int:
        if cantidad is None:
            raise ParametroFaltanteError("Las horas de reserva de sala son obligatorias.")
        try:
            horas = int(cantidad)
        except (ValueError, TypeError) as exc:
            raise DatoInvalidoError("Las horas de sala deben ser un número entero.") from exc
        if horas < 1 or horas > 12:
            raise DatoInvalidoError("La reserva de sala debe ser de entre 1 y 12 horas.")
        return horas

    def calcular_costo(
        self,
        cantidad: int,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        recargo_adicional: float = 0.0,
    ) -> float:
        horas = self.validar_parametros(cantidad)
        subtotal = self._tarifa_base * horas
        # Recargo del 5% si excede 6 horas continuas
        if horas > 6:
            subtotal *= 1.05
        return self._aplicar_reglas_financieras(subtotal, descuento, impuesto, recargo_adicional)

    @singledispatchmethod
    def cotizar_ajuste(self, ajuste) -> float:
        """Sobrecarga por tipo: acepta float (porcentaje extra) o int (recargo fijo)."""
        raise DatoInvalidoError(f"Tipo de ajuste no soportado: {type(ajuste).__name__}.")

    @cotizar_ajuste.register
    def _(self, porcentaje: float) -> float:
        if porcentaje < 0:
            raise DatoInvalidoError("El porcentaje de ajuste no puede ser negativo.")
        return round(self._tarifa_base * (1.0 + porcentaje), 2)

    @cotizar_ajuste.register
    def _(self, monto_fijo: int) -> float:
        if monto_fijo < 0:
            raise DatoInvalidoError("El monto fijo de ajuste no puede ser negativo.")
        return round(self._tarifa_base + monto_fijo, 2)

    def describir_servicio(self) -> str:
        return (
            f"Reserva de Sala '{self._nombre}' (Capacidad: {self._capacidad} personas, "
            f"cobro por hora)."
        )


class AlquilerEquipo(Servicio):
    """Servicio para alquiler de equipos tecnológicos (por días)."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        serial: str,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if serial is None:
            raise ParametroFaltanteError("El serial del equipo es obligatorio.")
        if not isinstance(serial, str) or len(serial.strip()) < 4:
            raise DatoInvalidoError("El serial del equipo debe tener al menos 4 caracteres.")
        self._serial = serial.strip().upper()

    @property
    def serial(self) -> str:
        return self._serial

    def validar_parametros(self, cantidad: int) -> int:
        if cantidad is None:
            raise ParametroFaltanteError("Los días de alquiler son obligatorios.")
        try:
            dias = int(cantidad)
        except (ValueError, TypeError) as exc:
            raise DatoInvalidoError("Los días de alquiler deben ser un número entero.") from exc
        if dias < 1 or dias > 30:
            raise DatoInvalidoError("El alquiler de equipos permite entre 1 y 30 días.")
        return dias

    def calcular_costo(
        self,
        cantidad: int,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        recargo_adicional: float = 0.0,
    ) -> float:
        dias = self.validar_parametros(cantidad)
        subtotal = self._tarifa_base * dias
        # Descuento por paquete semanal (7 días o más)
        if dias >= 7:
            subtotal *= 0.90
        return self._aplicar_reglas_financieras(subtotal, descuento, impuesto, recargo_adicional)

    def describir_servicio(self) -> str:
        return (
            f"Alquiler de Equipo '{self._nombre}' [Serial: {self._serial}] "
            f"(cobro por día)."
        )


class AsesoriaEspecializada(Servicio):
    """Servicio para asesorías técnicas especializadas (por sesiones)."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        area_especialidad: str,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if area_especialidad is None:
            raise ParametroFaltanteError("El área de especialidad es obligatoria.")
        if not isinstance(area_especialidad, str) or len(area_especialidad.strip()) < 3:
            raise DatoInvalidoError("El área de especialidad debe tener al menos 3 caracteres.")
        self._area_especialidad = area_especialidad.strip()

    @property
    def area_especialidad(self) -> str:
        return self._area_especialidad

    def validar_parametros(self, cantidad: int) -> int:
        if cantidad is None:
            raise ParametroFaltanteError("El número de sesiones es obligatorio.")
        try:
            sesiones = int(cantidad)
        except (ValueError, TypeError) as exc:
            raise DatoInvalidoError("El número de sesiones debe ser un entero.") from exc
        if sesiones < 1 or sesiones > 20:
            raise DatoInvalidoError("Las asesorías se contratan entre 1 y 20 sesiones.")
        return sesiones

    def calcular_costo(
        self,
        cantidad: int,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        recargo_adicional: float = 0.0,
    ) -> float:
        sesiones = self.validar_parametros(cantidad)
        subtotal = self._tarifa_base * sesiones
        return self._aplicar_reglas_financieras(subtotal, descuento, impuesto, recargo_adicional)

    def describir_servicio(self) -> str:
        return (
            f"Asesoría Especializada '{self._nombre}' en {self._area_especialidad} "
            f"(cobro por sesión)."
        )


class Reserva(EntidadSistema):
    """Integra cliente, servicio, duración y estado, con confirmación y cancelación seguras."""

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        recargo_adicional: float = 0.0,
    ):
        super().__init__(id_reserva)

        if cliente is None or servicio is None:
            raise ParametroFaltanteError("La reserva exige un cliente y un servicio válidos.")
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El parámetro 'cliente' debe ser una instancia de Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El parámetro 'servicio' debe ser una instancia de Servicio.")

        if not cliente.activo:
            raise DisponibilidadError(
                f"El cliente '{cliente.nombre}' ({cliente.id}) está inactivo y no puede reservar."
            )
        if not servicio.disponible:
            raise DisponibilidadError(
                f"El servicio '{servicio.nombre}' ({servicio.id}) no está disponible."
            )

        duracion_validada = servicio.validar_parametros(duracion)
        total_calculado = servicio.calcular_costo(
            duracion_validada,
            descuento=descuento,
            impuesto=impuesto,
            recargo_adicional=recargo_adicional,
        )

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion_validada
        self._descuento = descuento
        self._impuesto = impuesto
        self._recargo_adicional = recargo_adicional
        self._total = total_calculado
        self._estado = "PENDIENTE"

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def total(self) -> float:
        return self._total

    def confirmar(self) -> None:
        if self._estado == "CANCELADA":
            raise OperacionReservaError(
                f"No se puede confirmar la reserva {self._id}: ya fue cancelada."
            )
        if self._estado == "CONFIRMADA":
            raise OperacionReservaError(
                f"La reserva {self._id} ya se encuentra confirmada."
            )
        self._estado = "CONFIRMADA"

    def cancelar(self) -> None:
        if self._estado == "CANCELADA":
            raise OperacionReservaError(
                f"La reserva {self._id} ya estaba cancelada previamente."
            )
        self._estado = "CANCELADA"

    def resumen(self) -> str:
        return (
            f"Reserva[{self._id}] | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Duración: {self._duracion} | "
            f"Total: ${self._total:,.2f} | Estado: {self._estado}"
        )