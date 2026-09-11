"""Mismos colores que `infra/excel_styles.py`, para que el semáforo se vea igual en
la tabla de la app y en el Excel que después abre el Validador."""

from __future__ import annotations

from PySide6.QtGui import QColor

from airandes_migrador.core.common.validacion import Semaforo

_COLOR_HEX = {
    Semaforo.ROJO: "#FFC7CE",
    Semaforo.NARANJA: "#FFE0B2",
    Semaforo.VERDE: "#C6EFCE",
}


def color_para_semaforo(semaforo: Semaforo) -> QColor:
    return QColor(_COLOR_HEX[semaforo])
