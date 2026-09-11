"""Tipos de resultado de validación compartidos entre los dominios Herramientas y Stock."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Semaforo(str, Enum):
    ROJO = "ROJO"
    NARANJA = "NARANJA"
    VERDE = "VERDE"


class Veredicto(str, Enum):
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    PENDIENTE = "PENDIENTE"


@dataclass
class ResultadoValidacion:
    """Resultado de evaluar una fila contra el motor de reglas de un dominio."""

    semaforo: Semaforo
    veredicto: Veredicto
    observaciones: list[str] = field(default_factory=list)
    fila_ref: str = ""

    @property
    def es_transferible(self) -> bool:
        return self.veredicto is Veredicto.APROBADO

    def agregar_observacion(self, texto: str) -> None:
        if texto and texto not in self.observaciones:
            self.observaciones.append(texto)

    def texto_observaciones(self) -> str:
        return " | ".join(self.observaciones)


@dataclass
class ResumenValidacion:
    """Conteo agregado tras correr el motor de reglas sobre un archivo completo."""

    total: int = 0
    aprobadas: int = 0
    pendientes: int = 0
    rechazadas: int = 0


@dataclass
class ResumenTransferencia:
    """Resultado de correr la transferencia al maestro sobre un archivo completo."""

    transferidas: int = 0
    omitidas_ya_transferidas: int = 0
    omitidas_no_aprobadas: int = 0
