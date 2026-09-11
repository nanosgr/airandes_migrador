"""Conversión tolerante de valores numéricos y de fecha leídos de Excel: el Cargador
puede haber tipeado un número o una fecha como texto, así que no alcanza con confiar
en el tipo que trae la celda."""

from __future__ import annotations

from datetime import date, datetime

from dateutil import parser as _date_parser


def a_fecha_opcional(valor: object) -> date | None:
    """openpyxl devuelve celdas de fecha como `datetime`; el Cargador puede haber
    tipeado la fecha como texto ('2026-06-01', '01/06/2026'). Si no se puede
    interpretar como fecha, devuelve None en vez de propagar un dato inválido al
    motor de reglas (mejor "sin fecha" que un crash o una fecha inventada)."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return _date_parser.parse(str(valor).strip(), dayfirst=True).date()
    except (ValueError, TypeError, OverflowError):
        return None


def a_entero_opcional(valor: object) -> int | None:
    if valor is None or valor == "" or isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float):
        return int(valor)
    try:
        return int(str(valor).strip())
    except (ValueError, TypeError):
        try:
            return int(float(str(valor).strip().replace(",", ".")))
        except (ValueError, TypeError):
            return None


def a_flotante_opcional(valor: object) -> float | None:
    if valor is None or valor == "" or isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        return float(str(valor).strip().replace(",", "."))
    except (ValueError, TypeError):
        return None
