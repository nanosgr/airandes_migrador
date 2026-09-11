"""No hay login: se pide el nombre del operador una sola vez (persistido en
QSettings) para las columnas de auditoría TRANSFERIDO_POR, ya que una misma PC
puede ser compartida por Cargador y Validador."""

from __future__ import annotations

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QInputDialog, QWidget

_CLAVE_OPERADOR = "operador/nombre"


def obtener_operador(parent: QWidget) -> str:
    settings = QSettings()
    nombre_guardado = settings.value(_CLAVE_OPERADOR, "", str)
    if nombre_guardado:
        return nombre_guardado
    return cambiar_operador(parent)


def cambiar_operador(parent: QWidget) -> str:
    settings = QSettings()
    actual = settings.value(_CLAVE_OPERADOR, "", str)
    nombre, aceptado = QInputDialog.getText(
        parent,
        "Operador",
        "Ingresá tu nombre (queda registrado en la auditoría de transferencias):",
        text=actual,
    )
    nombre = nombre.strip()
    if aceptado and nombre:
        settings.setValue(_CLAVE_OPERADOR, nombre)
        return nombre
    return actual or "Desconocido"
