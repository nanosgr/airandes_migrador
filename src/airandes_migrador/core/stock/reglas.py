"""Módulo C — motor de validación de Stock: traducción literal del orden de
evaluación del pseudocódigo `ValidarYTransferirStock` (sección 2 del SRS/Metodología
de Stock), con dos ajustes de negocio confirmados el 2026-09-11:

1. La lista de campos obligatorios es la completa del SRS 2.3 (9 campos), no la
   lista corta del pseudocódigo simplificado (4 campos).
2. El caso NARANJA (saldo <= 0) nunca se autotransfiere: queda PENDIENTE de
   aprobación manual explícita del Validador, igual que en el pseudocódigo original
   (que tampoco lo pasa por `CopiarAMaestroCavok`).
"""

from __future__ import annotations

from airandes_migrador.core.common.validacion import ResultadoValidacion, Semaforo, Veredicto
from airandes_migrador.core.stock.config import CatalogosStock
from airandes_migrador.core.stock.modelo import FilaStock

_ETIQUETAS_OBLIGATORIOS = {
    "nombre": "NOMBRE",
    "categoria": "CATEGORÍA",
    "tipo": "TIPO",
    "xyz": "XYZ",
    "deposito": "DEPÓSITO",
    "ubicacion": "UBICACIÓN",
    "cantidad": "CANTIDAD",
    "unidad": "UNIDAD",
    "moneda": "MONEDA",
}


def _valor_vacio(valor: object) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def validar_obligatorios(
    fila: FilaStock, catalogos: CatalogosStock
) -> ResultadoValidacion | None:
    faltantes = [
        _ETIQUETAS_OBLIGATORIOS[campo]
        for campo in catalogos.campos_obligatorios
        if _valor_vacio(getattr(fila, campo, None))
    ]
    if not faltantes:
        return None
    return ResultadoValidacion(
        semaforo=Semaforo.ROJO,
        veredicto=Veredicto.RECHAZADO,
        observaciones=["Faltan campos obligatorios para Cavok (" + ", ".join(faltantes) + ")"],
        fila_ref=fila.clave_natural,
    )


def validar_serializado(fila: FilaStock) -> ResultadoValidacion | None:
    if not fila.es_serializado:
        return None
    if _valor_vacio(fila.sn) or _valor_vacio(fila.estado):
        return ResultadoValidacion(
            semaforo=Semaforo.ROJO,
            veredicto=Veredicto.RECHAZADO,
            observaciones=["Componente serializado requiere SN y Estado"],
            fila_ref=fila.clave_natural,
        )
    return None


def validar_saldo(fila: FilaStock) -> ResultadoValidacion | None:
    """Regla de Exclusión de Negativos (SRS 2.3): stock <= 0 nunca se autotransfiere,
    queda pendiente de ajuste/aprobación manual del auditor."""
    saldo_no_positivo = fila.cantidad_negativa or (
        fila.cantidad is not None and fila.cantidad <= 0
    )
    if not saldo_no_positivo:
        return None
    return ResultadoValidacion(
        semaforo=Semaforo.NARANJA,
        veredicto=Veredicto.PENDIENTE,
        observaciones=["Stock negativo en ClaseX. Requiere ajuste previo."],
        fila_ref=fila.clave_natural,
    )


def evaluar_fila_stock(fila: FilaStock, catalogos: CatalogosStock) -> ResultadoValidacion:
    resultado = validar_obligatorios(fila, catalogos)
    if resultado is not None:
        return resultado

    resultado = validar_serializado(fila)
    if resultado is not None:
        return resultado

    resultado = validar_saldo(fila)
    if resultado is not None:
        return resultado

    return ResultadoValidacion(
        semaforo=Semaforo.VERDE,
        veredicto=Veredicto.APROBADO,
        fila_ref=fila.clave_natural,
    )
