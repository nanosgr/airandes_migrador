from __future__ import annotations

from airandes_migrador.core.herramientas.normalizacion import meses_a_dias, normalizar_fabricante


def test_alias_cdi_se_normaliza(fabricantes_alias):
    assert (
        normalizar_fabricante("CDI", fabricantes_alias.alias)
        == "CONSOLIDATED DEVICES INC (CDI)"
    )


def test_alias_consolidated_devices_inc_se_normaliza(fabricantes_alias):
    assert (
        normalizar_fabricante("Consolidated Devices Inc", fabricantes_alias.alias)
        == "CONSOLIDATED DEVICES INC (CDI)"
    )


def test_alias_bristool_se_normaliza_a_britool(fabricantes_alias):
    assert normalizar_fabricante("BRISTOOL", fabricantes_alias.alias) == "BRITOOL"
    assert normalizar_fabricante("britool", fabricantes_alias.alias) == "BRITOOL"


def test_alias_delco_se_normaliza_a_ac_delco(fabricantes_alias):
    assert normalizar_fabricante("Delco", fabricantes_alias.alias) == "AC DELCO"


def test_fabricante_desconocido_queda_en_mayusculas(fabricantes_alias):
    assert normalizar_fabricante("snap-on", fabricantes_alias.alias) == "SNAP-ON"


def test_fabricante_vacio_o_none_devuelve_none(fabricantes_alias):
    assert normalizar_fabricante(None, fabricantes_alias.alias) is None
    assert normalizar_fabricante("   ", fabricantes_alias.alias) is None


def test_doce_meses_son_365_dias():
    assert meses_a_dias(12) == 365


def test_seis_meses_son_182_o_183_dias():
    assert meses_a_dias(6) in (182, 183)
