"""Lectura de hojas Excel con validación estricta de encabezado.

Deliberadamente NO usa `pandas.read_excel(...).to_excel(...)` como round-trip: eso
reconstruye la hoja entera y destruye validaciones de datos, formato condicional y
columnas que el Cargador dejó en Excel. En cambio, se abre con openpyxl y se lee
celda por celda, devolviendo también el número de fila real de cada registro para
que la capa de escritura pueda volver exactamente a esa fila.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import openpyxl
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from airandes_migrador.core.common.excepciones import ErrorEncabezadoExcel


def abrir_hoja(ruta: Path, nombre_hoja: str, solo_lectura: bool = False) -> tuple[Workbook, Worksheet]:
    if not ruta.exists():
        raise ErrorEncabezadoExcel(f"No se encontró el archivo '{ruta}'.")
    wb = openpyxl.load_workbook(ruta, read_only=solo_lectura, data_only=True, keep_vba=False)
    if nombre_hoja not in wb.sheetnames:
        raise ErrorEncabezadoExcel(
            f"El archivo '{ruta.name}' no tiene una hoja llamada '{nombre_hoja}'. "
            f"Hojas disponibles: {', '.join(wb.sheetnames)}"
        )
    return wb, wb[nombre_hoja]


def leer_encabezado(hoja: Worksheet) -> list[Any]:
    primera_fila = next(hoja.iter_rows(min_row=1, max_row=1, values_only=True), ())
    return list(primera_fila)


def validar_encabezado(hoja: Worksheet, columnas_esperadas: list[str], nombre_archivo: str) -> None:
    encabezado = leer_encabezado(hoja)
    encontrado = encabezado[: len(columnas_esperadas)]
    if encontrado != columnas_esperadas:
        raise ErrorEncabezadoExcel(
            f"El encabezado de '{nombre_archivo}' no coincide con el esperado por la app.\n"
            f"Esperado : {columnas_esperadas}\n"
            f"Encontrado: {encontrado}"
        )


def indices_columnas(hoja: Worksheet, columnas: list[str]) -> dict[str, int]:
    """Devuelve {nombre columna: índice 1-indexado} tal como los espera openpyxl."""
    encabezado = leer_encabezado(hoja)
    indice: dict[str, int] = {}
    for nombre in columnas:
        if nombre not in encabezado:
            raise ErrorEncabezadoExcel(f"No se encontró la columna '{nombre}' en el encabezado.")
        indice[nombre] = encabezado.index(nombre) + 1
    return indice


def indices_columnas_opcionales(hoja: Worksheet, columnas: list[str]) -> dict[str, int]:
    """Como `indices_columnas`, pero solo devuelve las columnas que efectivamente
    existen en el encabezado, en vez de fallar si falta alguna. Se usa para columnas
    auxiliares que el Cargador puede o no haber agregado a la planilla de trabajo."""
    encabezado = leer_encabezado(hoja)
    return {nombre: encabezado.index(nombre) + 1 for nombre in columnas if nombre in encabezado}


def _fila_vacia(valores: dict[str, Any]) -> bool:
    return all(v is None or (isinstance(v, str) and not v.strip()) for v in valores.values())


def leer_filas_como_dicts(
    hoja: Worksheet, columnas: list[str]
) -> list[tuple[int, dict[str, Any]]]:
    """Devuelve [(número de fila Excel 1-indexado, {columna: valor})], saltando filas
    completamente vacías (usa `hoja.max_row`, que openpyxl acota al último dato real,
    por lo que no recorre miles de filas en blanco de más)."""
    indice = indices_columnas(hoja, columnas)
    registros: list[tuple[int, dict[str, Any]]] = []
    for numero_fila, fila in enumerate(
        hoja.iter_rows(min_row=2, max_col=max(indice.values())), start=2
    ):
        valores = {nombre: fila[idx - 1].value for nombre, idx in indice.items()}
        if _fila_vacia(valores):
            continue
        registros.append((numero_fila, valores))
    return registros
