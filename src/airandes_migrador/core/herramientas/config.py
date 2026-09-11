"""Modelos y carga de los catálogos configurables del módulo Herramientas
(config/catalogos_herramientas.yaml y config/fabricantes_alias.yaml)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field

from airandes_migrador.core.common.config_loader import cargar_yaml_validado


class CatalogosHerramientas(BaseModel):
    sede: str
    bases: list[str]
    unidades: list[str]
    ubicaciones: list[str]
    estados: list[str]
    empresas_calibradoras: list[str]
    campos_obligatorios: list[str]
    intervalo_dias_default: int = 365
    alerta_dias_default: int = 30
    estados_vencida_bloqueantes: list[str]
    estados_vencida_pendientes: list[str]


class FabricantesAlias(BaseModel):
    alias: dict[str, str] = Field(default_factory=dict)


@dataclass
class ConfigHerramientas:
    catalogos: CatalogosHerramientas
    fabricantes_alias: FabricantesAlias


def cargar_config_herramientas(directorio_config: Path) -> ConfigHerramientas:
    catalogos = cargar_yaml_validado(
        directorio_config / "catalogos_herramientas.yaml", CatalogosHerramientas
    )
    fabricantes = cargar_yaml_validado(
        directorio_config / "fabricantes_alias.yaml", FabricantesAlias
    )
    return ConfigHerramientas(catalogos=catalogos, fabricantes_alias=fabricantes)
