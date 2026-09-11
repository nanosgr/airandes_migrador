"""Normalización de FABRICANTE (SRS 3.3) y conversión del intervalo de calibración
que GEMA entrega en meses a los días que usa el maestro Cavok."""

from __future__ import annotations


def normalizar_fabricante(texto_crudo: str | None, alias: dict[str, str]) -> str | None:
    """Aplica el diccionario de alias (config/fabricantes_alias.yaml). Si no hay
    coincidencia, cae al comportamiento por defecto del pseudocódigo: MAYÚSCULAS del
    texto original. La comparación ignora mayúsculas/minúsculas y espacios sobrantes
    para tolerar variantes de tipeo, sin cambiar la semántica del pseudocódigo."""
    if texto_crudo is None:
        return None
    texto = texto_crudo.strip()
    if not texto:
        return None
    alias_normalizado = {clave.strip().upper(): valor for clave, valor in alias.items()}
    return alias_normalizado.get(texto.upper(), texto.upper())


def meses_a_dias(meses: int) -> int:
    """Convierte un intervalo de calibración expresado en meses (como lo entrega GEMA)
    a días (como lo requiere INTERVALO_DÍAS del maestro). 12 meses -> 365 días."""
    return round(meses * 365 / 12)
