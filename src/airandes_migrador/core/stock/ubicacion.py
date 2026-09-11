"""Módulo B (SRS Stock 2.2 / Metodología 2.2): inyección masiva de ubicaciones
físicas por defecto para no bloquear la carga inicial de las filas sin posición
registrada en pañol (~3.561 de 5.058 filas según el diagnóstico del proyecto)."""

from __future__ import annotations

from airandes_migrador.core.common.texto import combinar_observaciones
from airandes_migrador.core.stock.modelo import FilaStock

OBSERVACION_UBICACION_INYECTADA = (
    "Sin posición en pañol: se asignó ubicación por defecto, requiere ordenamiento físico"
)


def aplicar_ubicacion_por_defecto(fila: FilaStock, ubicacion_por_defecto: str) -> bool:
    """Si `fila.ubicacion` está vacía/nula/en blanco, la reemplaza por
    `ubicacion_por_defecto` y deja una advertencia en OBSERVACIONES. Devuelve True si
    se aplicó la inyección (para que el llamador pueda contar filas afectadas)."""
    if fila.ubicacion is not None and fila.ubicacion.strip():
        return False
    fila.ubicacion = ubicacion_por_defecto
    fila.observaciones = combinar_observaciones(
        fila.observaciones, OBSERVACION_UBICACION_INYECTADA
    )
    return True
