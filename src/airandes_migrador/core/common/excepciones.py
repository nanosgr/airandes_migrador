"""Excepciones propias del dominio, para distinguir errores esperables (de datos/config)
de bugs. La UI las captura para mostrar mensajes claros al Cargador/Validador."""

from __future__ import annotations


class ErrorAirandesMigrador(Exception):
    """Base de todas las excepciones del paquete."""


class ErrorConfiguracion(ErrorAirandesMigrador):
    """Un archivo de configuración (config/*.yaml) es inválido o le falta una clave."""


class ErrorEncabezadoExcel(ErrorAirandesMigrador):
    """El encabezado de una hoja Excel no coincide con el esperado por la app."""


class ErrorTransferencia(ErrorAirandesMigrador):
    """No se pudo completar la transferencia de una fila al maestro final."""
