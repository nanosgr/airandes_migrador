from __future__ import annotations

from airandes_migrador.core.common.validacion import Semaforo, Veredicto
from airandes_migrador.core.stock.reglas import evaluar_fila_stock


def test_fila_valida_completa_queda_aprobada(fila_stock_valida, catalogos_stock):
    resultado = evaluar_fila_stock(fila_stock_valida(), catalogos_stock)
    assert resultado.semaforo is Semaforo.VERDE
    assert resultado.veredicto is Veredicto.APROBADO


def test_falta_nombre_es_rojo(fila_stock_valida, catalogos_stock):
    resultado = evaluar_fila_stock(fila_stock_valida(nombre=None), catalogos_stock)
    assert resultado.semaforo is Semaforo.ROJO
    assert resultado.veredicto is Veredicto.RECHAZADO
    assert "NOMBRE" in resultado.texto_observaciones()


def test_falta_categoria_tipo_o_xyz_es_rojo(fila_stock_valida, catalogos_stock):
    resultado = evaluar_fila_stock(fila_stock_valida(categoria=None), catalogos_stock)
    assert resultado.semaforo is Semaforo.ROJO
    assert "CATEGORÍA" in resultado.texto_observaciones()


def test_falta_moneda_es_rojo_lista_completa_srs(fila_stock_valida, catalogos_stock):
    # Este campo NO está en el pseudocódigo corto pero sí en el SRS 2.3 -> debe fallar.
    resultado = evaluar_fila_stock(fila_stock_valida(moneda=None), catalogos_stock)
    assert resultado.semaforo is Semaforo.ROJO
    assert "MONEDA" in resultado.texto_observaciones()


def test_serializado_sin_sn_es_rojo(fila_stock_valida, catalogos_stock):
    fila = fila_stock_valida(es_serializado=True, sn=None, estado="Disponible")
    resultado = evaluar_fila_stock(fila, catalogos_stock)
    assert resultado.semaforo is Semaforo.ROJO
    assert "SN y Estado" in resultado.texto_observaciones()


def test_serializado_sin_estado_es_rojo(fila_stock_valida, catalogos_stock):
    fila = fila_stock_valida(es_serializado=True, sn="12345", estado=None)
    resultado = evaluar_fila_stock(fila, catalogos_stock)
    assert resultado.semaforo is Semaforo.ROJO


def test_serializado_con_sn_y_estado_es_aprobado(fila_stock_valida, catalogos_stock):
    fila = fila_stock_valida(es_serializado=True, sn="12345", estado="Disponible")
    resultado = evaluar_fila_stock(fila, catalogos_stock)
    assert resultado.veredicto is Veredicto.APROBADO


def test_cantidad_negativa_flag_es_naranja_pendiente_no_autotransferible(
    fila_stock_valida, catalogos_stock
):
    fila = fila_stock_valida(cantidad_negativa=True)
    resultado = evaluar_fila_stock(fila, catalogos_stock)
    assert resultado.semaforo is Semaforo.NARANJA
    assert resultado.veredicto is Veredicto.PENDIENTE
    assert not resultado.es_transferible


def test_cantidad_cero_tambien_requiere_aprobacion_manual(fila_stock_valida, catalogos_stock):
    fila = fila_stock_valida(cantidad=0)
    resultado = evaluar_fila_stock(fila, catalogos_stock)
    assert resultado.veredicto is Veredicto.PENDIENTE


def test_cantidad_negativa_numerica_es_pendiente(fila_stock_valida, catalogos_stock):
    fila = fila_stock_valida(cantidad=-5)
    resultado = evaluar_fila_stock(fila, catalogos_stock)
    assert resultado.veredicto is Veredicto.PENDIENTE


def test_prioridad_serializado_sobre_saldo_negativo(fila_stock_valida, catalogos_stock):
    # El pseudocódigo evalúa serializado ANTES que saldo negativo (ELIF).
    fila = fila_stock_valida(es_serializado=True, sn=None, cantidad_negativa=True)
    resultado = evaluar_fila_stock(fila, catalogos_stock)
    assert resultado.semaforo is Semaforo.ROJO
    assert "SN y Estado" in resultado.texto_observaciones()
