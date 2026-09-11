"""Modelo de una fila del maestro de Stock de Productos (hoja `STOCK` de
STOCK_CAVOK.xlsx, 20 columnas). El orden de `COLUMNAS` es el orden REAL del template
destino, verificado leyendo el archivo — la hoja real tiene columnas vacías extra
hasta la Z que no forman parte del template y deben ignorarse."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import date
from typing import Optional

from airandes_migrador.core.common.numeros import a_fecha_opcional, a_flotante_opcional

_CAMPOS_FECHA = {"fecha_de_vencimiento"}
_CAMPOS_FLOTANTES = {"cantidad", "valor_unitario"}

COLUMNAS: list[tuple[str, str]] = [
    ("NOMBRE", "nombre"),
    ("PN", "pn"),
    ("SN", "sn"),
    ("PN_ALT", "pn_alt"),
    ("CATEGORÍA", "categoria"),
    ("TIPO", "tipo"),
    ("XYZ", "xyz"),
    ("C123", "c123"),
    ("FABRICANTE", "fabricante"),
    ("ESTADO", "estado"),
    ("SEDE", "sede"),
    ("DEPÓSITO", "deposito"),
    ("UBICACIÓN", "ubicacion"),
    ("LOTE", "lote"),
    ("FECHA_DE_VENCIMIENTO", "fecha_de_vencimiento"),
    ("CANTIDAD", "cantidad"),
    ("UNIDAD DE MEDIDA", "unidad"),
    ("MONEDA", "moneda"),
    ("VALOR_UNITARIO", "valor_unitario"),
    ("OBSERVACIONES", "observaciones"),
]

NOMBRES_COLUMNAS_EXCEL: list[str] = [col for col, _ in COLUMNAS]
_ATRIBUTO_POR_COLUMNA: dict[str, str] = dict(COLUMNAS)


@dataclass
class FilaStock:
    nombre: Optional[str] = None
    pn: Optional[str] = None
    sn: Optional[str] = None
    pn_alt: Optional[str] = None
    categoria: Optional[str] = None
    tipo: Optional[str] = None
    xyz: Optional[str] = None
    c123: Optional[str] = None
    fabricante: Optional[str] = None
    estado: Optional[str] = None
    sede: Optional[str] = None
    deposito: Optional[str] = None
    ubicacion: Optional[str] = None
    lote: Optional[str] = None
    fecha_de_vencimiento: Optional[date] = None
    cantidad: Optional[float] = None
    unidad: Optional[str] = None
    moneda: Optional[str] = None
    valor_unitario: Optional[float] = None
    observaciones: Optional[str] = None

    # Flags de negocio, NO son columnas del maestro: se completan durante la carga
    # cruzando con las hojas auxiliares de trazabilidad (PorSerie -> es_serializado,
    # hoja "Revisar_stock_negativo" -> cantidad_negativa) antes de evaluar el Módulo C.
    es_serializado: bool = False
    cantidad_negativa: bool = False

    # Datos crudos de ClaseX usados por el Módulo A (clasificación), no viajan al maestro.
    familia_claseX: Optional[str] = None
    nodo_contable_claseX: Optional[str] = None

    @property
    def clave_natural(self) -> str:
        """Clave para idempotencia. El stock no tiene un único ID natural fuerte: el
        mismo artículo (mismo PN/SN/LOTE) aparece una vez por depósito con stock
        propio (ej. DEPOSITO CENTRAL y CORDOBA), así que DEPÓSITO es parte de la
        clave -- de lo contrario la segunda fila del mismo artículo en otro depósito
        se descartaría como "ya transferida"."""
        return "|".join(
            [
                (self.deposito or "").strip(),
                (self.pn or "").strip(),
                (self.sn or "").strip(),
                (self.lote or "").strip(),
            ]
        )

    def a_fila_excel(self) -> list:
        return [getattr(self, attr) for _, attr in COLUMNAS]

    @classmethod
    def desde_dict_por_columna(cls, valores: dict[str, object]) -> "FilaStock":
        nombres_validos = {f.name for f in fields(cls)}
        kwargs = {}
        for columna, valor in valores.items():
            atributo = _ATRIBUTO_POR_COLUMNA.get(columna)
            if atributo in nombres_validos:
                valor = None if valor == "" else valor
                if atributo in _CAMPOS_FECHA:
                    valor = a_fecha_opcional(valor)
                elif atributo in _CAMPOS_FLOTANTES:
                    valor = a_flotante_opcional(valor)
                kwargs[atributo] = valor
        return cls(**kwargs)
