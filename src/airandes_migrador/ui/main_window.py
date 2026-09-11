"""Ventana principal: navegación entre Inicio, Herramientas y Stock vía
`QStackedWidget`. Se prefiere sobre `QWizard` porque el flujo real necesita volver
atrás y recalcular libremente (no es un asistente lineal de un solo sentido)."""

from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from airandes_migrador.ui.common.operador import cambiar_operador
from airandes_migrador.ui.herramientas.vista import VistaHerramientas
from airandes_migrador.ui.home_view import VistaInicio
from airandes_migrador.ui.stock.vista import VistaStock


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Migrador AIRANDES → Cavok")
        self.resize(1100, 720)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._vista_inicio = VistaInicio()
        self._vista_inicio.modulo_elegido.connect(self._ir_a_modulo)
        self._vista_herramientas = VistaHerramientas()
        self._vista_stock = VistaStock()

        self._stack.addWidget(self._vista_inicio)
        self._stack.addWidget(self._vista_herramientas)
        self._stack.addWidget(self._vista_stock)

        self._crear_menu()

    def _crear_menu(self) -> None:
        menu = self.menuBar().addMenu("Navegación")

        accion_inicio = QAction("Ir a Inicio", self)
        accion_inicio.triggered.connect(lambda: self._stack.setCurrentWidget(self._vista_inicio))
        menu.addAction(accion_inicio)

        accion_herramientas = QAction("Herramientas Calibradas", self)
        accion_herramientas.triggered.connect(lambda: self._ir_a_modulo("herramientas"))
        menu.addAction(accion_herramientas)

        accion_stock = QAction("Stock de Productos", self)
        accion_stock.triggered.connect(lambda: self._ir_a_modulo("stock"))
        menu.addAction(accion_stock)

        menu.addSeparator()
        accion_operador = QAction("Cambiar operador…", self)
        accion_operador.triggered.connect(lambda: cambiar_operador(self))
        menu.addAction(accion_operador)

    def _ir_a_modulo(self, modulo: str) -> None:
        if modulo == "herramientas":
            self._stack.setCurrentWidget(self._vista_herramientas)
        elif modulo == "stock":
            self._stack.setCurrentWidget(self._vista_stock)
