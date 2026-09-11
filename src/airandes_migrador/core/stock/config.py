"""Modelos y carga de los catálogos configurables del módulo Stock
(config/catalogos_stock.yaml, config/diccionario_categorias.yaml,
config/matriz_tipo_xyz.yaml)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

from airandes_migrador.core.common.config_loader import cargar_yaml_validado


class CatalogosStock(BaseModel):
    campos_obligatorios: list[str]
    ubicacion_por_defecto: str = "POR UBICAR"
    unidades_homologadas: dict[str, str] = Field(default_factory=dict)
    unidades_validas: list[str]
    monedas_validas: list[str]


class ReglaClasificacion(BaseModel):
    campo: Literal["familia", "nodo_contable"]
    valor: str
    categoria: Optional[str] = None
    tipo: Optional[str] = None
    xyz: Optional[str] = None


class DiccionarioClasificacion(BaseModel):
    """Estructura compartida por diccionario_categorias.yaml (aporta `categoria`) y
    matriz_tipo_xyz.yaml (aporta `tipo`/`xyz`): reglas ordenadas, gana la primera que
    matchea por familia o nodo contable."""

    reglas: list[ReglaClasificacion] = Field(default_factory=list)


@dataclass
class ConfigStock:
    catalogos: CatalogosStock
    diccionario_categorias: DiccionarioClasificacion
    matriz_tipo_xyz: DiccionarioClasificacion


def cargar_config_stock(directorio_config: Path) -> ConfigStock:
    catalogos = cargar_yaml_validado(directorio_config / "catalogos_stock.yaml", CatalogosStock)
    diccionario_categorias = cargar_yaml_validado(
        directorio_config / "diccionario_categorias.yaml", DiccionarioClasificacion
    )
    matriz_tipo_xyz = cargar_yaml_validado(
        directorio_config / "matriz_tipo_xyz.yaml", DiccionarioClasificacion
    )
    return ConfigStock(
        catalogos=catalogos,
        diccionario_categorias=diccionario_categorias,
        matriz_tipo_xyz=matriz_tipo_xyz,
    )
