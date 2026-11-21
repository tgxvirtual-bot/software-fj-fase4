from gestor import GestorSoftwareFJ
from modelos import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    Reserva,
    ReservaSala,
)


def simular_sistema() -> None:
    gestor = GestorSoftwareFJ(archivo_log="software_fj.log")
    print("=== INICIO DE SIMULACIÓN INTEGRAL - SOFTWARE FJ (SIN BASE DE DATOS) ===")

    # 1. Registro válido de cliente 1
    c1 = gestor.ejecutar_operacion(
        "1. Registrar cliente válido (C01)",
        lambda: gestor.registrar_cliente(
            Cliente("C01", "Laura Gómez", "laura.gomez@empresa.co", "3104567890", activo=True)
        ),
    )

    # 2. Registro válido de cliente 2
    c2 = gestor.ejecutar_operacion(
        "2. Registrar cliente válido (C02)",
        lambda: gestor.registrar_cliente(
            Cliente("C02", "Carlos Méndez", "carlos.mendez@correo.com", "3209876543", activo=True)
        ),
    )

    # 3. Registro inválido de cliente (correo mal formado)
    gestor.ejecutar_operacion(
        "3. Intentar registrar cliente con correo inválido (C03)",
        lambda: gestor.registrar_cliente(
            Cliente("C03", "Andrés Ruiz", "correo_sin_arroba", "3151112233", activo=True)
        ),
    )

    # 4. Registro válido de 3 servicios especializados (Sala, Equipo, Asesoría)
    s_sala = gestor.ejecutar_operacion(
        "4. Registrar servicio ReservaSala (S01)",
        lambda: gestor.registrar_servicio(
            ReservaSala("S01", "Sala Ejecutiva Norte", 45000, capacidad=12, disponible=True)
        ),
    )
    s_equipo = gestor.ejecutar_operacion(
        "5. Registrar servicio AlquilerEquipo (S02)",
        lambda: gestor.registrar_servicio(
            AlquilerEquipo("S02", "Laptop Workstation Pro", 80000, serial="SN-WK9901", disponible=True)
        ),
    )
    s_asesoria = gestor.ejecutar_operacion(
        "6. Registrar servicio AsesoriaEspecializada (S03)",
        lambda: gestor.registrar_servicio(
            AsesoriaEspecializada("S03", "Arquitectura Cloud y DevOps", 150000, "Cloud", disponible=True)
        ),
    )

    # 5. Creación incorrecta de servicio (tarifa base negativa / texto no numérico -> encadenamiento)
    gestor.ejecutar_operacion(
        "7. Intentar crear servicio con tarifa base inválida (S04)",
        lambda: gestor.registrar_servicio(
            AlquilerEquipo("S04", "Proyector 4K", "no_es_numero", serial="SN-PRJ04", disponible=True)
        ),
    )

    # 6. Reserva exitosa de sala (4 horas, sin descuento adicional)
    r1 = gestor.ejecutar_operacion(
        "8. Crear reserva válida de sala (R01)",
        lambda: gestor.crear_reserva(Reserva("R01", c1, s_sala, duracion=4)),
    )

    # 7. Reserva exitosa de equipo con descuento y confirmación
    r2 = gestor.ejecutar_operacion(
        "9. Crear y confirmar reserva válida de equipo (R02)",
        lambda: (
            lambda res: (res.confirmar(), res)[1]
        )(gestor.crear_reserva(Reserva("R02", c2, s_equipo, duracion=7, descuento=0.05))),
    )

    # 8. Reserva fallida por duración fuera de rango (15 horas > máximo 12 horas)
    gestor.ejecutar_operacion(
        "10. Intentar reserva de sala con duración inválida (15 horas)",
        lambda: gestor.crear_reserva(Reserva("R03", c1, s_sala, duracion=15)),
    )

    # 9. Reserva fallida por servicio no disponible
    if s_asesoria:
        s_asesoria.establecer_disponibilidad(False)
    gestor.ejecutar_operacion(
        "11. Intentar reserva de asesoría marcada como NO DISPONIBLE",
        lambda: gestor.crear_reserva(Reserva("R04", c1, s_asesoria, duracion=3)),
    )

    # 10. Operación no permitida: intentar confirmar una reserva ya confirmada
    if r2:
        gestor.ejecutar_operacion(
            "12. Intentar confirmar nuevamente una reserva ya CONFIRMADA (R02)",
            lambda: r2.confirmar(),
        )

    # Demostración adicional de sobrecarga en ReservaSala (si existe)
    if s_sala:
        print("\n--- Demostración de sobrecarga cotizar_ajuste ---")
        print("Ajuste +15% (float):", s_sala.cotizar_ajuste(0.15))
        print("Ajuste +$10,000 (int):", s_sala.cotizar_ajuste(10000))

    print("\n=== RESUMEN FINAL EN MEMORIA ===")
    print("Clientes registrados:", len(gestor.clientes))
    for c in gestor.clientes:
        print("  *", c.resumen())

    print("Servicios registrados:", len(gestor.servicios))
    for s in gestor.servicios:
        print("  *", s.resumen(), "->", s.describir_servicio())

    print("Reservas registradas:", len(gestor.reservas))
    for r in gestor.reservas:
        print("  *", r.resumen())

    print("\nSimulación finalizada. Revisa 'software_fj.log' para el historial de eventos y errores.")


if __name__ == "__main__":
    simular_sistema()