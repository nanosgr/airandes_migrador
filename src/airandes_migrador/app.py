"""Punto de entrada de la aplicación de escritorio (PySide6)."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from airandes_migrador.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setOrganizationName("AIRANDES")
    app.setApplicationName("Migrador Cavok")

    ventana = MainWindow()
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
