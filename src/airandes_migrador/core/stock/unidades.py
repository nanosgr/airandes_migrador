"""Homologación de unidades de medida y validación de moneda ISO 4217, según las
reglas de negocio 2.3 del SRS de Stock ("Regla de Homologación de Unidades")."""

from __future__ import annotations


def homologar_unidad(unidad_claseX: str | None, mapa: dict[str, str]) -> str | None:
    """Convierte una unidad de ClaseX (ej. 'UNID.', 'METROS') al código Cavok
    correspondiente (ej. 'UND', 'MT'). Si no hay mapeo conocido, devuelve el valor
    original en mayúsculas para no perder el dato, sin inventar una conversión."""
    if unidad_claseX is None:
        return None
    texto = unidad_claseX.strip()
    if not texto:
        return None
    mapa_normalizado = {clave.strip().upper(): valor for clave, valor in mapa.items()}
    return mapa_normalizado.get(texto.upper(), texto.upper())


def es_moneda_valida(moneda: str | None, monedas_validas: list[str]) -> bool:
    if moneda is None:
        return False
    return moneda.strip().upper() in {m.upper() for m in monedas_validas}
