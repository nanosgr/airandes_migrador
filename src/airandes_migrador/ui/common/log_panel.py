"""Panel de log de la sesión de trabajo: info/advertencia/error, con timestamp."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import QPlainTextEdit

_COLOR_POR_NIVEL = {
    "info": "#e0e0e0",
    "advertencia": "#e0a030",
    "error": "#ff6b6b",
}


class PanelLog(QPlainTextEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(5000)

    def info(self, texto: str) -> None:
        self._agregar(texto, "info")

    def advertencia(self, texto: str) -> None:
        self._agregar(texto, "advertencia")

    def error(self, texto: str) -> None:
        self._agregar(texto, "error")

    def _agregar(self, texto: str, nivel: str) -> None:
        hora = datetime.now().strftime("%H:%M:%S")
        color = _COLOR_POR_NIVEL[nivel]
        self.appendHtml(f'<span style="color:{color}">[{hora}] {texto}</span>')
