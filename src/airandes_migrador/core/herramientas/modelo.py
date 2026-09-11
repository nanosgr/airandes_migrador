"""Modelo de una fila del maestro de Herramientas Calibradas (hoja `Herramienta` de
Import_herramienta.xlsx, 36 columnas). El orden de `COLUMNAS` es el orden REAL del
template destino, verificado leyendo el archivo — la transferencia al maestro debe
respetarlo estrictamente."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import date
from typing import Optional

from airandes_migrador.core.common.numeros import (
    a_entero_opcional,
    a_fecha_opcional,
    a_flotante_opcional,
)

_CAMPOS_FECHA = {"ultima_calibracion", "fecha_dano", "fecha_descarte"}
_CAMPOS_ENTEROS = {"intervalo_dias", "alerta_dias"}
_CAMPOS_FLOTANTES = {"valor_total"}

# (nombre de columna en el Excel, nombre de atributo en FilaHerramienta), en orden real.
COLUMNAS: list[tuple[str, str]] = [
    ("SEDE", "sede"),
    ("BASE", "base"),
    ("NOMBRE", "nombre"),
    ("TIPO", "tipo"),
    ("FUNCIÓN/APLICABILIDAD", "funcion_aplicabilidad"),
    ("FABRICANTE", "fabricante"),
    ("PN", "pn"),
    ("SN", "sn"),
    ("CODIGO", "codigo"),
    ("MODELOS", "modelos"),
    ("UNIDAD", "unidad"),
    ("UBICACIÓN", "ubicacion"),
    ("ESTADO", "estado"),
    ("INTERVALO_DÍAS", "intervalo_dias"),
    ("ALERTA_DÍAS", "alerta_dias"),
    ("ÚLTIMA_CALIBRACIÓN", "ultima_calibracion"),
    ("EMPRESA CALIBRADORA", "empresa_calibradora"),
    ("N° INFORME DE CALIBRACIÓN", "numero_informe_calibracion"),
    ("TIPO CALIBRACIÓN", "tipo_calibracion"),
    ("RANGO", "rango"),
    ("UNIDAD_RANGO", "unidad_rango"),
    ("PATRÓN_UTILIZADO", "patron_utilizado"),
    ("MODELO", "modelo"),
    ("OBSERVACIONES", "observaciones"),
    ("PN_ALT", "pn_alt"),
    ("VALOR_TOTAL", "valor_total"),
    ("ROTO", "roto"),
    ("FECHA_DAÑO", "fecha_dano"),
    ("FECHA_DESCARTE", "fecha_descarte"),
    ("ALERTA_FECHA_DESCARTE", "alerta_fecha_descarte"),
    ("ERRORES_MEDICIÓN", "errores_medicion"),
    ("ERRORES_LÍMITES_ACEPTABLES", "errores_limites_aceptables"),
    ("POSESIÓN", "posesion"),
    ("PROCEDENCIA", "procedencia"),
    ("TIPO_DATO_TÉCNICO", "tipo_dato_tecnico"),
    ("NÚMERO_DOC_DATO_TÉCNICO", "numero_doc_dato_tecnico"),
]

NOMBRES_COLUMNAS_EXCEL: list[str] = [col for col, _ in COLUMNAS]
_ATRIBUTO_POR_COLUMNA: dict[str, str] = dict(COLUMNAS)
_COLUMNA_POR_ATRIBUTO: dict[str, str] = {attr: col for col, attr in COLUMNAS}


@dataclass
class FilaHerramienta:
    sede: Optional[str] = None
    base: Optional[str] = None
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    funcion_aplicabilidad: Optional[str] = None
    fabricante: Optional[str] = None
    pn: Optional[str] = None
    sn: Optional[str] = None
    codigo: Optional[str] = None
    modelos: Optional[str] = None
    unidad: Optional[str] = None
    ubicacion: Optional[str] = None
    estado: Optional[str] = None
    intervalo_dias: Optional[int] = None
    alerta_dias: Optional[int] = None
    ultima_calibracion: Optional[date] = None
    empresa_calibradora: Optional[str] = None
    numero_informe_calibracion: Optional[str] = None
    tipo_calibracion: Optional[str] = None
    rango: Optional[str] = None
    unidad_rango: Optional[str] = None
    patron_utilizado: Optional[str] = None
    modelo: Optional[str] = None
    observaciones: Optional[str] = None
    pn_alt: Optional[str] = None
    valor_total: Optional[float] = None
    roto: Optional[str] = None
    fecha_dano: Optional[date] = None
    fecha_descarte: Optional[date] = None
    alerta_fecha_descarte: Optional[str] = None
    errores_medicion: Optional[str] = None
    errores_limites_aceptables: Optional[str] = None
    posesion: Optional[str] = None
    procedencia: Optional[str] = None
    tipo_dato_tecnico: Optional[str] = None
    numero_doc_dato_tecnico: Optional[str] = None

    @property
    def clave_natural(self) -> str:
        """Clave usada para idempotencia: el SN es obligatorio y único por instrumento."""
        return (self.sn or "").strip()

    def a_fila_excel(self) -> list:
        """Valores en el orden exacto de COLUMNAS, listos para escribir en el maestro."""
        return [getattr(self, attr) for _, attr in COLUMNAS]

    @classmethod
    def desde_dict_por_columna(cls, valores: dict[str, object]) -> "FilaHerramienta":
        """Construye una fila a partir de un dict {nombre columna Excel: valor}."""
        nombres_validos = {f.name for f in fields(cls)}
        kwargs = {}
        for columna, valor in valores.items():
            atributo = _ATRIBUTO_POR_COLUMNA.get(columna)
            if atributo in nombres_validos:
                valor = None if valor == "" else valor
                if atributo in _CAMPOS_FECHA:
                    valor = a_fecha_opcional(valor)
                elif atributo in _CAMPOS_ENTEROS:
                    valor = a_entero_opcional(valor)
                elif atributo in _CAMPOS_FLOTANTES:
                    valor = a_flotante_opcional(valor)
                kwargs[atributo] = valor
        return cls(**kwargs)
