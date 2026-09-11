"""Módulo A (SRS Stock 2.1 / Metodología 2.1): normalización y mapeo automático de
CATEGORÍA/TIPO/XYZ a partir de Familia y NodoContable de ClaseX, vía las tablas de
equivalencia configurables (config/diccionario_categorias.yaml, matriz_tipo_xyz.yaml).
Sin coincidencia -> CATEGORÍA="General" + bandera de revisión humana."""

from __future__ import annotations

from dataclasses import dataclass

from airandes_migrador.core.stock.config import DiccionarioClasificacion, ReglaClasificacion

CATEGORIA_SIN_MATCH = "General"


@dataclass
class ResultadoClasificacion:
    categoria: str | None
    tipo: str | None
    xyz: str | None
    requiere_revision_humana: bool


def _buscar_regla(
    reglas: list[ReglaClasificacion], familia: str | None, nodo_contable: str | None
) -> ReglaClasificacion | None:
    valores_fila = {"familia": familia, "nodo_contable": nodo_contable}
    for regla in reglas:
        valor_fila = valores_fila.get(regla.campo)
        if valor_fila and valor_fila.strip().upper() == regla.valor.strip().upper():
            return regla
    return None


def clasificar_fila(
    familia: str | None,
    nodo_contable: str | None,
    diccionario_categorias: DiccionarioClasificacion,
    matriz_tipo_xyz: DiccionarioClasificacion,
) -> ResultadoClasificacion:
    regla_categoria = _buscar_regla(diccionario_categorias.reglas, familia, nodo_contable)
    regla_tipo_xyz = _buscar_regla(matriz_tipo_xyz.reglas, familia, nodo_contable)

    categoria = regla_categoria.categoria if regla_categoria else None
    tipo = regla_tipo_xyz.tipo if regla_tipo_xyz else None
    xyz = regla_tipo_xyz.xyz if regla_tipo_xyz else None

    requiere_revision = categoria is None or tipo is None or xyz is None
    if categoria is None:
        categoria = CATEGORIA_SIN_MATCH

    return ResultadoClasificacion(
        categoria=categoria, tipo=tipo, xyz=xyz, requiere_revision_humana=requiere_revision
    )
