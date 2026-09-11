"""Ejecuta una función del `core` en un hilo aparte: generar la matriz de validación
o transferir al maestro puede tardar varios segundos (o más de un minuto para las
5.058 filas de Stock), y correrlo en el hilo principal congelaría la ventana."""

from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import QThread, Signal


class TareaEnHilo(QThread):
    completada = Signal(object)
    fallo = Signal(str)

    def __init__(self, funcion: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._funcion = funcion
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            resultado = self._funcion(*self._args, **self._kwargs)
        except Exception as exc:  # noqa: BLE001 - se muestra en la UI, no se relanza
            self.fallo.emit(str(exc))
        else:
            self.completada.emit(resultado)
