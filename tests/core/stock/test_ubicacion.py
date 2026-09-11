from __future__ import annotations

from airandes_migrador.core.stock.modelo import FilaStock
from airandes_migrador.core.stock.ubicacion import aplicar_ubicacion_por_defecto


def test_ubicacion_vacia_se_reemplaza_por_defecto():
    fila = FilaStock(ubicacion=None)
    aplicado = aplicar_ubicacion_por_defecto(fila, "POR UBICAR")
    assert aplicado is True
    assert fila.ubicacion == "POR UBICAR"
    assert "ordenamiento físico" in fila.observaciones


def test_ubicacion_en_blanco_se_reemplaza():
    fila = FilaStock(ubicacion="   ")
    aplicar_ubicacion_por_defecto(fila, "POR UBICAR")
    assert fila.ubicacion == "POR UBICAR"


def test_ubicacion_ya_completa_no_se_toca():
    fila = FilaStock(ubicacion="ESTANTE A1")
    aplicado = aplicar_ubicacion_por_defecto(fila, "POR UBICAR")
    assert aplicado is False
    assert fila.ubicacion == "ESTANTE A1"
    assert fila.observaciones is None
