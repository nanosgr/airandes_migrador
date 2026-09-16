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

# Las celdas de la tabla siempre llevan uno de los fondos pastel de arriba (pensados
# para texto oscuro encima), sin importar si la app está en modo claro u oscuro. Por
# eso el texto de esas celdas se fija a este color en vez de heredar el color de texto
# de la paleta general: con la paleta oscura, el texto por defecto es claro y quedaría
# ilegible sobre esos fondos.
COLOR_TEXTO_TABLA = QColor("#1a1a1a")


def color_para_semaforo(semaforo: Semaforo) -> QColor:
    return QColor(_COLOR_HEX[semaforo])
