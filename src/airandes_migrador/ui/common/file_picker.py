"""Selector de archivo reutilizable: campo de solo lectura con la ruta elegida + botón
"Examinar…". Se usa tanto para elegir el archivo de trabajo (abrir) como el maestro
destino (abrir, porque ya debe existir con el encabezado correcto)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget

FILTRO_EXCEL = "Archivos Excel (*.xlsx *.xlsm)"


class SelectorArchivo(QWidget):
    cambiado = Signal(str)

    def __init__(self, titulo_dialogo: str, filtro: str = FILTRO_EXCEL, parent=None) -> None:
        super().__init__(parent)
        self._titulo_dialogo = titulo_dialogo
        self._filtro = filtro

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._campo = QLineEdit()
        self._campo.setReadOnly(True)
        self._campo.setPlaceholderText("Ningún archivo seleccionado")
        boton = QPushButton("Examinar…")
        boton.clicked.connect(self._elegir_archivo)
        layout.addWidget(self._campo, stretch=1)
        layout.addWidget(boton)

    def _elegir_archivo(self) -> None:
        ruta, _ = QFileDialog.getOpenFileName(self, self._titulo_dialogo, "", self._filtro)
        if ruta:
            self.set_ruta(ruta)

    def ruta(self) -> Path | None:
        texto = self._campo.text().strip()
        return Path(texto) if texto else None

    def set_ruta(self, ruta: str) -> None:
        self._campo.setText(ruta)
        self.cambiado.emit(ruta)
