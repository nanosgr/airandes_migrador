"""Tema oscuro de la aplicación.

Se aplica explícitamente (paleta + hoja de estilos) en vez de heredar el estilo nativo
de la plataforma, por dos motivos:

1. En Windows, el estilo nativo ("windowsvista") no seguía el tema oscuro del sistema
   operativo: la ventana se veía siempre con fondo blanco, sin importar la
   configuración de Windows 11. Con la app tan clara sobre un escritorio oscuro, la
   tipografía de la tabla resultaba incómoda de leer (demasiado contraste/brillo).
2. El estilo nativo de Windows además ignora buena parte de `QPalette` para botones y
   combos, así que para tener un tema oscuro consistente hace falta el estilo
   "Fusion", que sí respeta la paleta en todas las plataformas.
"""

from __future__ import annotations

import sys

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget

# Colores base del tema. Se mantienen aparte de `ui/common/colores.py`: esos son los
# colores de semáforo (fondos claros pensados para texto oscuro encima, ver
# `ModeloTablaEvaluacion.data()`), independientes del tema general de la app.
_FONDO = QColor("#1e1e1e")
_FONDO_ALTERNO = QColor("#252526")
_BASE = QColor("#252526")
_TEXTO = QColor("#e0e0e0")
_TEXTO_DESHABILITADO = QColor("#787878")
_BOTON = QColor("#3a3a3a")
_RESALTADO = QColor("#3a6ea5")
_RESALTADO_TEXTO = QColor("#ffffff")
_BORDE = "#3f3f3f"
_ENCABEZADO_FONDO = "#2d2d30"

_HOJA_ESTILOS = f"""
QWidget {{
    font-size: 10.5pt;
}}
QMainWindow::separator {{
    background-color: {_BORDE};
}}
QGroupBox {{
    border: 1px solid {_BORDE};
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}}
QTableView {{
    gridline-color: {_BORDE};
    selection-background-color: {_RESALTADO.name()};
    selection-color: {_RESALTADO_TEXTO.name()};
    alternate-background-color: {_FONDO_ALTERNO.name()};
    font-size: 10.5pt;
}}
QTableView::item {{
    padding: 5px;
}}
QHeaderView::section {{
    background-color: {_ENCABEZADO_FONDO};
    color: {_TEXTO.name()};
    padding: 6px;
    border: none;
    border-right: 1px solid {_BORDE};
    border-bottom: 1px solid {_BORDE};
    font-weight: 600;
}}
QLineEdit, QComboBox, QPlainTextEdit {{
    background-color: {_BASE.name()};
    border: 1px solid {_BORDE};
    border-radius: 3px;
    padding: 3px;
}}
QPushButton {{
    background-color: {_BOTON.name()};
    border: 1px solid {_BORDE};
    border-radius: 3px;
    padding: 5px 12px;
}}
QPushButton:hover {{
    background-color: #454545;
}}
QPushButton:pressed {{
    background-color: #2a2a2a;
}}
QPushButton:disabled {{
    color: {_TEXTO_DESHABILITADO.name()};
}}
"""


def aplicar_tema_oscuro(app: QApplication) -> None:
    app.setStyle("Fusion")

    paleta = QPalette()
    paleta.setColor(QPalette.ColorRole.Window, _FONDO)
    paleta.setColor(QPalette.ColorRole.WindowText, _TEXTO)
    paleta.setColor(QPalette.ColorRole.Base, _BASE)
    paleta.setColor(QPalette.ColorRole.AlternateBase, _FONDO_ALTERNO)
    paleta.setColor(QPalette.ColorRole.ToolTipBase, _TEXTO)
    paleta.setColor(QPalette.ColorRole.ToolTipText, _TEXTO)
    paleta.setColor(QPalette.ColorRole.Text, _TEXTO)
    paleta.setColor(QPalette.ColorRole.Button, _BOTON)
    paleta.setColor(QPalette.ColorRole.ButtonText, _TEXTO)
    paleta.setColor(QPalette.ColorRole.BrightText, QColor("#ff6b6b"))
    paleta.setColor(QPalette.ColorRole.Link, QColor("#5fa8ff"))
    paleta.setColor(QPalette.ColorRole.Highlight, _RESALTADO)
    paleta.setColor(QPalette.ColorRole.HighlightedText, _RESALTADO_TEXTO)
    paleta.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, _TEXTO_DESHABILITADO
    )
    paleta.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, _TEXTO_DESHABILITADO
    )
    paleta.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, _TEXTO_DESHABILITADO
    )
    app.setPalette(paleta)
    app.setStyleSheet(_HOJA_ESTILOS)


def aplicar_titulo_oscuro_windows(ventana: QWidget) -> None:
    """En Windows pone también la barra de título nativa en modo oscuro (vía DWM), para
    que no quede una franja blanca arriba de la ventana sobre un escritorio oscuro. No
    hace nada en otras plataformas. Requiere que la ventana ya tenga handle nativo
    (llamar después de `show()`)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        hwnd = int(ventana.winId())
        valor = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(valor), ctypes.sizeof(valor)
        )
    except OSError:
        pass
