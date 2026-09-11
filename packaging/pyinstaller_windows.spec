# -*- mode: python ; coding: utf-8 -*-
# Build (desde la raíz del proyecto, EN Windows): uv run pyinstaller packaging/pyinstaller_windows.spec
# Genera dist\airandes-migrador\: copiar esa carpeta junto con config\ al equipo destino.
# PyInstaller no cross-compila: este build corre EN Windows (no se puede generar el
# .exe desde Linux).

from pathlib import Path

RAIZ = Path(SPECPATH).resolve().parent

a = Analysis(
    [str(RAIZ / "src" / "airandes_migrador" / "app.py")],
    pathex=[str(RAIZ / "src")],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="airandes-migrador",
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="airandes-migrador",
)
