"""Carga y validación de los catálogos configurables (config/*.yaml).

Los archivos YAML los edita gente que no programa (Cargador/Validador), así que
cualquier error de formato debe traducirse a un mensaje claro en español, no a un
traceback de pydantic. `cargar_yaml_validado` es el único punto de entrada: lee el
archivo, lo valida contra un modelo pydantic y devuelve la instancia ya tipada.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from airandes_migrador.core.common.excepciones import ErrorConfiguracion

ModeloT = TypeVar("ModeloT", bound=BaseModel)


def cargar_yaml_crudo(ruta: Path) -> dict:
    if not ruta.exists():
        raise ErrorConfiguracion(
            f"No se encontró el archivo de configuración '{ruta}'. "
            "Verificá que la carpeta config/ esté junto al ejecutable."
        )
    try:
        with ruta.open("r", encoding="utf-8") as f:
            contenido = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ErrorConfiguracion(
            f"El archivo '{ruta.name}' tiene un error de formato YAML: {exc}"
        ) from exc
    if contenido is None:
        contenido = {}
    if not isinstance(contenido, dict):
        raise ErrorConfiguracion(
            f"El archivo '{ruta.name}' debe contener un mapeo clave: valor en la raíz."
        )
    return contenido


def cargar_yaml_validado(ruta: Path, modelo: type[ModeloT]) -> ModeloT:
    contenido = cargar_yaml_crudo(ruta)
    try:
        return modelo.model_validate(contenido)
    except ValidationError as exc:
        errores = "; ".join(
            f"campo '{'.'.join(str(p) for p in e['loc'])}': {e['msg']}" for e in exc.errors()
        )
        raise ErrorConfiguracion(
            f"El archivo '{ruta.name}' tiene datos inválidos -> {errores}"
        ) from exc
