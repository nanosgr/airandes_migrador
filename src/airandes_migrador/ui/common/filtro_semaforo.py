"""Filtro "solo ROJO/NARANJA/VERDE" sobre la tabla de revisión, para que el
Validador pueda enfocarse en lo que falta corregir sin scrollear miles de filas VERDE."""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel

from airandes_migrador.core.common.validacion import Semaforo


class ProxyFiltroSemaforo(QSortFilterProxyModel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._semaforo_filtro: Semaforo | None = None

    def set_filtro_semaforo(self, semaforo: Semaforo | None) -> None:
        self._semaforo_filtro = semaforo
        self.invalidateFilter()

    def filterAcceptsRow(
        self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex
    ) -> bool:
        if self._semaforo_filtro is None:
            return True
        fila_evaluada = self.sourceModel().fila_evaluada_en(source_row)
        return fila_evaluada.resultado.semaforo == self._semaforo_filtro
