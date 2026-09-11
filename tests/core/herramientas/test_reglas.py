from __future__ import annotations

from datetime import date

from airandes_migrador.core.common.validacion import Semaforo, Veredicto
from airandes_migrador.core.herramientas.reglas import evaluar_fila

FECHA_ACTUAL = date(2026, 9, 3)  # tal como especifica el pseudocódigo del SRS


def test_fila_valida_y_no_vencida_queda_aprobada(fila_herramienta_valida, catalogos_herramientas):
    fila = fila_herramienta_valida(ultima_calibracion=date(2026, 6, 1), intervalo_dias=365)
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    assert resultado.semaforo is Semaforo.VERDE
    assert resultado.veredicto is Veredicto.APROBADO


def test_falta_sn_es_rojo_y_rechazado(fila_herramienta_valida, catalogos_herramientas):
    fila = fila_herramienta_valida(sn=None)
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    assert resultado.semaforo is Semaforo.ROJO
    assert resultado.veredicto is Veredicto.RECHAZADO
    assert "SN" in resultado.texto_observaciones()


def test_falta_ubicacion_en_blanco_es_rojo(fila_herramienta_valida, catalogos_herramientas):
    fila = fila_herramienta_valida(ubicacion="   ")
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    assert resultado.semaforo is Semaforo.ROJO


def test_obligatorios_incompletos_corta_antes_de_evaluar_vencimiento(
    fila_herramienta_valida, catalogos_herramientas
):
    # Vencida Y sin SN: debe reportar solo el error de obligatorios (Regla 1 corta).
    fila = fila_herramienta_valida(
        sn=None, ultima_calibracion=date(2020, 1, 1), intervalo_dias=365, estado="Calibrada"
    )
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    assert resultado.veredicto is Veredicto.RECHAZADO
    assert "obligatorios" in resultado.texto_observaciones().lower()


def test_vencida_con_estado_calibrada_es_error_bloqueante(
    fila_herramienta_valida, catalogos_herramientas
):
    fila = fila_herramienta_valida(
        ultima_calibracion=date(2020, 1, 1), intervalo_dias=365, estado="Calibrada"
    )
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    assert resultado.semaforo is Semaforo.NARANJA
    assert resultado.veredicto is Veredicto.RECHAZADO
    assert "no puede ingresar" in resultado.texto_observaciones()


def test_vencida_con_estado_disponible_es_error_bloqueante(
    fila_herramienta_valida, catalogos_herramientas
):
    fila = fila_herramienta_valida(
        ultima_calibracion=date(2020, 1, 1), intervalo_dias=365, estado="Disponible"
    )
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    assert resultado.veredicto is Veredicto.RECHAZADO


def test_vencida_con_estado_no_disponible_queda_pendiente_no_autoaprobada(
    fila_herramienta_valida, catalogos_herramientas
):
    fila = fila_herramienta_valida(
        ultima_calibracion=date(2020, 1, 1), intervalo_dias=365, estado="No disponible"
    )
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    assert resultado.semaforo is Semaforo.NARANJA
    assert resultado.veredicto is Veredicto.PENDIENTE
    assert not resultado.es_transferible


def test_vencida_con_estado_en_reparacion_queda_pendiente(
    fila_herramienta_valida, catalogos_herramientas
):
    fila = fila_herramienta_valida(
        ultima_calibracion=date(2020, 1, 1), intervalo_dias=365, estado="En reparación"
    )
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    assert resultado.veredicto is Veredicto.PENDIENTE


def test_sin_fecha_ultima_calibracion_no_evalua_vencimiento(
    fila_herramienta_valida, catalogos_herramientas
):
    fila = fila_herramienta_valida(ultima_calibracion=None)
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    assert resultado.veredicto is Veredicto.APROBADO


def test_intervalo_por_defecto_se_usa_si_fila_no_trae_intervalo(
    fila_herramienta_valida, catalogos_herramientas
):
    fila = fila_herramienta_valida(ultima_calibracion=date(2026, 8, 1), intervalo_dias=None)
    resultado = evaluar_fila(fila, catalogos_herramientas, FECHA_ACTUAL)
    # 2026-08-01 + 365 días por defecto está muy en el futuro: no vencida.
    assert resultado.veredicto is Veredicto.APROBADO
