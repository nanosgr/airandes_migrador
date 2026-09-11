"""Pantalla de inicio: elegir entre el módulo de Herramientas Calibradas y el de
Stock de Productos."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class VistaInicio(QWidget):
    modulo_elegido = Signal(str)  # "herramientas" | "stock"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addStretch(1)

        titulo = QLabel("<h1>Migrador AIRANDES → Cavok</h1>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Elegí el módulo de migración a trabajar:")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        boton_herramientas = QPushButton("Herramientas Calibradas")
        boton_herramientas.setMinimumHeight(48)
        boton_herramientas.clicked.connect(lambda: self.modulo_elegido.emit("herramientas"))
        layout.addWidget(boton_herramientas)

        boton_stock = QPushButton("Stock de Productos")
        boton_stock.setMinimumHeight(48)
        boton_stock.clicked.connect(lambda: self.modulo_elegido.emit("stock"))
        layout.addWidget(boton_stock)

        layout.addStretch(1)
