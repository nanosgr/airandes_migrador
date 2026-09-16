"""Punto de entrada de la aplicación de escritorio (PySide6)."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from airandes_migrador.ui.common.tema import aplicar_tema_oscuro, aplicar_titulo_oscuro_windows
from airandes_migrador.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setOrganizationName("AIRANDES")
    app.setApplicationName("Migrador Cavok")
    aplicar_tema_oscuro(app)

    ventana = MainWindow()
    ventana.show()
    aplicar_titulo_oscuro_windows(ventana)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
