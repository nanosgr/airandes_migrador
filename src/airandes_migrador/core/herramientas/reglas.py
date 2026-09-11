"""Motor de reglas de Herramientas Calibradas: traducción literal del pseudocódigo de
la sección 3 de "Especificacion Tecnica - Automatizacion Migracion Herramientas
Calibradas.docx" (Regla 1: obligatorios, Regla 2: vencimiento metrológico), más la
normalización de fabricante (Regla 3, aplicada aparte en normalizacion.py durante la
carga, no durante la validación).

Orden de evaluación: Regla 1 corta la evaluación con ROJO si falla (no tiene sentido
evaluar el vencimiento de una fila con datos incompletos), igual que en el motor de
Stock. Si Regla 1 pasa, se evalúa Regla 2."""

from __future__ import annotations

from datetime import date, timedelta

from airandes_migrador.core.common.validacion import ResultadoValidacion, Semaforo, Veredicto
from airandes_migrador.core.herramientas.config import CatalogosHerramientas
from airandes_migrador.core.herramientas.modelo import FilaHerramienta

_ETIQUETAS_OBLIGATORIOS = {
    "sede": "SEDE",
    "base": "BASE",
    "nombre": "NOMBRE",
    "sn": "SN",
    "unidad": "UNIDAD",
    "ubicacion": "UBICACIÓN",
}


def _valor_vacio(valor: object) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def validar_obligatorios(
    fila: FilaHerramienta, catalogos: CatalogosHerramientas
) -> ResultadoValidacion | None:
    """Regla 1 (SRS 3.1). Devuelve un resultado ROJO si falta algún obligatorio,
    o None si la fila los tiene todos (para que evaluar_fila siga con Regla 2)."""
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
        observaciones=[
            "ERROR: Campos obligatorios incompletos (" + ", ".join(faltantes) + ")"
        ],
        fila_ref=fila.clave_natural,
    )


def validar_vencimiento(
    fila: FilaHerramienta, catalogos: CatalogosHerramientas, fecha_actual: date
) -> ResultadoValidacion | None:
    """Regla 2 (SRS 3.2). Devuelve None si la herramienta no está vencida (o no se
    puede calcular el vencimiento por falta de fecha), en cuyo caso no aporta semáforo
    propio y evaluar_fila la considera VERDE si nada más la objetó."""
    if fila.ultima_calibracion is None:
        return None
    intervalo_dias = fila.intervalo_dias or catalogos.intervalo_dias_default
    fecha_vencimiento = fila.ultima_calibracion + timedelta(days=intervalo_dias)
    if fecha_vencimiento >= fecha_actual:
        return None

    estado = (fila.estado or "").strip()
    if estado in catalogos.estados_vencida_bloqueantes:
        return ResultadoValidacion(
            semaforo=Semaforo.NARANJA,
            veredicto=Veredicto.RECHAZADO,
            observaciones=[
                "ERROR: Herramienta vencida no puede ingresar como Calibrada/Disponible"
            ],
            fila_ref=fila.clave_natural,
        )
    # Vencida pero ya reflejada como No disponible / En reparación: no se autoaprueba,
    # el Validador debe confirmarla explícitamente (decisión de negocio 2026-09-11).
    return ResultadoValidacion(
        semaforo=Semaforo.NARANJA,
        veredicto=Veredicto.PENDIENTE,
        observaciones=["ADVERTENCIA: Registrada como No Disponible / En Reparación"],
        fila_ref=fila.clave_natural,
    )


def evaluar_fila(
    fila: FilaHerramienta, catalogos: CatalogosHerramientas, fecha_actual: date
) -> ResultadoValidacion:
    resultado = validar_obligatorios(fila, catalogos)
    if resultado is not None:
        return resultado

    resultado = validar_vencimiento(fila, catalogos, fecha_actual)
    if resultado is not None:
        return resultado

    return ResultadoValidacion(
        semaforo=Semaforo.VERDE,
        veredicto=Veredicto.APROBADO,
        fila_ref=fila.clave_natural,
    )
