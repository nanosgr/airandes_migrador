"""Persistencia de auditoría e idempotencia de transferencias, en SQLite.

Es la fuente de verdad para saber si una fila ya fue transferida al maestro final,
robusta a que el archivo intermedio se copie o renombre (a diferencia de solo mirar
una columna dentro del propio Excel, que también se escribe como respaldo legible).
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS transferencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dominio TEXT NOT NULL,              -- 'herramientas' | 'stock'
    fila_key TEXT NOT NULL,             -- clave natural: SN (herramientas) / PN|SN|LOTE (stock)
    archivo_origen TEXT NOT NULL,
    fecha_hora TEXT NOT NULL,
    usuario TEXT NOT NULL,
    UNIQUE(dominio, fila_key)
);
"""


@dataclass
class RegistroTransferencia:
    dominio: str
    fila_key: str
    archivo_origen: str
    fecha_hora: str
    usuario: str


class AuditoriaDB:
    """Wrapper delgado sobre sqlite3. Una instancia por sesión de la app o del CLI."""

    def __init__(self, ruta_db: Path) -> None:
        self._ruta_db = ruta_db
        ruta_db.parent.mkdir(parents=True, exist_ok=True)
        with self._conectar() as con:
            con.executescript(_ESQUEMA)

    @contextmanager
    def _conectar(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self._ruta_db)
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def ya_transferida(self, dominio: str, fila_key: str) -> bool:
        with self._conectar() as con:
            fila = con.execute(
                "SELECT 1 FROM transferencias WHERE dominio = ? AND fila_key = ?",
                (dominio, fila_key),
            ).fetchone()
            return fila is not None

    def registrar_transferencia(
        self, dominio: str, fila_key: str, archivo_origen: str, usuario: str
    ) -> RegistroTransferencia:
        fecha_hora = datetime.now().isoformat(timespec="seconds")
        with self._conectar() as con:
            con.execute(
                "INSERT INTO transferencias (dominio, fila_key, archivo_origen, fecha_hora, usuario) "
                "VALUES (?, ?, ?, ?, ?)",
                (dominio, fila_key, archivo_origen, fecha_hora, usuario),
            )
        return RegistroTransferencia(dominio, fila_key, archivo_origen, fecha_hora, usuario)
