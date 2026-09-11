"""Utilidades de texto compartidas entre los dominios Herramientas y Stock."""

from __future__ import annotations


def combinar_observaciones(original: str | None, nuevas: str) -> str:
    """Agrega `nuevas` al texto de observaciones existente sin duplicar ni perder lo
    que ya había escrito el Cargador."""
    original = (original or "").strip()
    if not nuevas:
        return original
    if not original:
        return nuevas
    if nuevas in original:
        return original
    return f"{original} | {nuevas}"
