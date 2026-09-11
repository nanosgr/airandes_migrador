from __future__ import annotations

from airandes_migrador.core.stock.unidades import es_moneda_valida, homologar_unidad

MAPA = {"UNID.": "UND", "METROS": "MT"}


def test_homologa_unid_a_und():
    assert homologar_unidad("UNID.", MAPA) == "UND"


def test_homologa_metros_a_mt():
    assert homologar_unidad("METROS", MAPA) == "MT"


def test_unidad_ya_homologada_no_se_altera_mas_alla_de_mayusculas():
    assert homologar_unidad("UND", MAPA) == "UND"


def test_unidad_desconocida_devuelve_mayusculas_sin_inventar():
    assert homologar_unidad("cajas", MAPA) == "CAJAS"


def test_moneda_valida():
    assert es_moneda_valida("usd", ["USD", "ARS", "EUR"])


def test_moneda_invalida():
    assert not es_moneda_valida("GBP", ["USD", "ARS", "EUR"])


def test_moneda_none_es_invalida():
    assert not es_moneda_valida(None, ["USD", "ARS", "EUR"])
