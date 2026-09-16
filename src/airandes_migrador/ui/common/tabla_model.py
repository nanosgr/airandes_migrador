"""Modelo de tabla genérico para mostrar filas evaluadas (Herramientas o Stock) con
color de semáforo. Usa `QAbstractTableModel` propio en vez de `QStandardItem` por
celda: para las 5.058 filas de Stock, crear miles de QStandardItem sería notablemente
más lento y consumiría mucha más memoria que envolver directamente la lista de
`FilaEvaluada` que ya devuelve el core."""

from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt

from airandes_migrador.ui.common.colores import COLOR_TEXTO_TABLA, color_para_semaforo

# Cada columna: (título mostrado, función que extrae el valor de una FilaEvaluada).
ColumnaTabla = tuple[str, Callable[[Any], Any]]


class ModeloTablaEvaluacion(QAbstractTableModel):
    def __init__(self, columnas: list[ColumnaTabla], parent=None) -> None:
        super().__init__(parent)
        self._columnas = columnas
        self._filas: list[Any] = []

    def actualizar_filas(self, filas: list[Any]) -> None:
        self.beginResetModel()
        self._filas = filas
        self.endResetModel()

    def fila_evaluada_en(self, row: int) -> Any:
        return self._filas[row]

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._filas)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._columnas)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        fila_evaluada = self._filas[index.row()]
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            _, extractor = self._columnas[index.column()]
            valor = extractor(fila_evaluada)
            return "" if valor is None else str(valor)
        if role == Qt.ItemDataRole.BackgroundRole:
            return color_para_semaforo(fila_evaluada.resultado.semaforo)
        if role == Qt.ItemDataRole.ForegroundRole:
            return COLOR_TEXTO_TABLA
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._columnas[section][0]
        return str(section + 1)
