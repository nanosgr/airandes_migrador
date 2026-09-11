"""Resuelve dónde está la carpeta `config/` (catálogos YAML editables), tanto en
modo desarrollo (ejecutando desde el repo con `uv run`) como empaquetado con
PyInstaller (donde el código vive en un directorio temporal distinto de donde se
distribuye `config/` junto al ejecutable)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def directorio_config_por_defecto() -> Path:
    variable_entorno = os.environ.get("AIRANDES_CONFIG_DIR")
    if variable_entorno:
        return Path(variable_entorno)

    if getattr(sys, "frozen", False):
        # Empaquetado con PyInstaller --onedir: config/ se distribuye junto al ejecutable.
        return Path(sys.executable).resolve().parent / "config"

    # Modo desarrollo: subir desde este archivo hasta encontrar la carpeta config/
    # hermana de src/ (raíz del proyecto).
    for ancestro in Path(__file__).resolve().parents:
        candidato = ancestro / "config"
        if candidato.is_dir():
            return candidato

    raise FileNotFoundError(
        "No se pudo encontrar la carpeta 'config/'. Definí la variable de entorno "
        "AIRANDES_CONFIG_DIR apuntando a ella."
    )


def directorio_datos_app() -> Path:
    """Carpeta persistente para la base de auditoría (SQLite) y `QSettings`,
    independiente del directorio de instalación (que puede ser de solo lectura)."""
    base = os.environ.get("AIRANDES_DATA_DIR")
    if base:
        return Path(base)
    if sys.platform == "win32":
        raiz = os.environ.get("APPDATA", str(Path.home()))
    else:
        raiz = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(raiz) / "airandes_migrador"
