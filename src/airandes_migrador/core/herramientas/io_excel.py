"""Orquesta la lectura del archivo de trabajo del Cargador, la generación de la
matriz de validación (con semáforos/observaciones/colores) y la transferencia de las
filas aprobadas al maestro `Import_herramienta.xlsx`, hoja `Herramienta`.

No reescribe la hoja completa con pandas: abre con openpyxl y solo toca las celdas
que le corresponden (FABRICANTE normalizado, OBSERVACIONES, columnas de auditoría),
preservando todo lo demás tal como lo dejó el Cargador."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from airandes_migrador.core.common.texto import combinar_observaciones
from airandes_migrador.core.common.validacion import (
    ResultadoValidacion,
    ResumenTransferencia,
    ResumenValidacion,
    Veredicto,
)
from airandes_migrador.core.herramientas.config import ConfigHerramientas
from airandes_migrador.core.herramientas.modelo import NOMBRES_COLUMNAS_EXCEL, FilaHerramienta
from airandes_migrador.core.herramientas.normalizacion import normalizar_fabricante
from airandes_migrador.core.herramientas.reglas import evaluar_fila
from airandes_migrador.infra import excel_reader, excel_writer
from airandes_migrador.infra.db import AuditoriaDB
from airandes_migrador.infra.excel_styles import aplicar_fill_fila

HOJA_HERRAMIENTA = "Herramienta"
DOMINIO = "herramientas"

# Columnas propias de la app, agregadas al final de la matriz de validación (no
# existen en el archivo de trabajo original ni se escriben en el maestro final).
COLUMNAS_AUDITORIA = ["SEMAFORO", "ESTADO_VALIDACION", "TRANSFERIDO_EL", "TRANSFERIDO_POR"]


@dataclass
class FilaEvaluada:
    fila_excel: int
    fila: FilaHerramienta
    resultado: ResultadoValidacion


def leer_filas_trabajo(
    ruta: Path, hoja: str = HOJA_HERRAMIENTA
) -> list[tuple[int, FilaHerramienta]]:
    _, ws = excel_reader.abrir_hoja(ruta, hoja, solo_lectura=True)
    excel_reader.validar_encabezado(ws, NOMBRES_COLUMNAS_EXCEL, ruta.name)
    registros = excel_reader.leer_filas_como_dicts(ws, NOMBRES_COLUMNAS_EXCEL)
    return [(num, FilaHerramienta.desde_dict_por_columna(valores)) for num, valores in registros]


def generar_matriz_validacion(
    ruta_entrada: Path,
    ruta_salida_matriz: Path,
    config: ConfigHerramientas,
    fecha_actual: date,
    hoja: str = HOJA_HERRAMIENTA,
) -> tuple[list[FilaEvaluada], ResumenValidacion]:
    """Lee `ruta_entrada` (01_Trabajo_Calibradas o el extract de precarga), aplica
    Regla 3 (normalización de fabricante) y evalúa Reglas 1/2 fila por fila. Escribe
    el resultado en `ruta_salida_matriz` (puede ser la misma ruta o una copia nueva):
    fabricante normalizado, observaciones de validación, semáforo/veredicto y color
    de fila."""
    wb, ws = excel_reader.abrir_hoja(ruta_entrada, hoja, solo_lectura=False)
    excel_reader.validar_encabezado(ws, NOMBRES_COLUMNAS_EXCEL, ruta_entrada.name)
    registros = excel_reader.leer_filas_como_dicts(ws, NOMBRES_COLUMNAS_EXCEL)

    indice_auditoria = excel_writer.agregar_columnas_si_faltan(ws, COLUMNAS_AUDITORIA)
    indice_datos = excel_reader.indices_columnas(ws, ["FABRICANTE", "OBSERVACIONES"])

    evaluadas: list[FilaEvaluada] = []
    conteos = {Veredicto.APROBADO: 0, Veredicto.PENDIENTE: 0, Veredicto.RECHAZADO: 0}
    ultima_columna_datos = len(NOMBRES_COLUMNAS_EXCEL)

    for numero_fila, valores in registros:
        fila = FilaHerramienta.desde_dict_por_columna(valores)
        fila.fabricante = normalizar_fabricante(fila.fabricante, config.fabricantes_alias.alias)
        resultado = evaluar_fila(fila, config.catalogos, fecha_actual)
        fila.observaciones = combinar_observaciones(
            fila.observaciones, resultado.texto_observaciones()
        )
        conteos[resultado.veredicto] += 1

        ws.cell(row=numero_fila, column=indice_datos["FABRICANTE"], value=fila.fabricante)
        ws.cell(row=numero_fila, column=indice_datos["OBSERVACIONES"], value=fila.observaciones)
        excel_writer.escribir_valores_fila(
            ws,
            numero_fila,
            indice_auditoria,
            {
                "SEMAFORO": resultado.semaforo.value,
                "ESTADO_VALIDACION": resultado.veredicto.value,
            },
        )
        aplicar_fill_fila(ws, numero_fila, 1, ultima_columna_datos, resultado.semaforo)

        evaluadas.append(FilaEvaluada(numero_fila, fila, resultado))

    excel_writer.guardar(wb, ruta_salida_matriz)

    resumen = ResumenValidacion(
        total=len(evaluadas),
        aprobadas=conteos[Veredicto.APROBADO],
        pendientes=conteos[Veredicto.PENDIENTE],
        rechazadas=conteos[Veredicto.RECHAZADO],
    )
    return evaluadas, resumen


def transferir_aprobadas(
    ruta_matriz: Path,
    ruta_maestro: Path,
    usuario: str,
    audit_db: AuditoriaDB,
    hoja: str = HOJA_HERRAMIENTA,
) -> ResumenTransferencia:
    """Copia al maestro las filas con veredicto APROBADO de `ruta_matriz` que todavía
    no fueron transferidas (idempotente: chequea SQLite y la columna TRANSFERIDO_EL).
    """
    columnas_matriz = NOMBRES_COLUMNAS_EXCEL + COLUMNAS_AUDITORIA
    wb_matriz, ws_matriz = excel_reader.abrir_hoja(ruta_matriz, hoja, solo_lectura=False)
    registros = excel_reader.leer_filas_como_dicts(ws_matriz, columnas_matriz)
    indice_auditoria = excel_reader.indices_columnas(ws_matriz, COLUMNAS_AUDITORIA)

    wb_maestro, ws_maestro = excel_reader.abrir_hoja(ruta_maestro, hoja, solo_lectura=False)
    excel_reader.validar_encabezado(ws_maestro, NOMBRES_COLUMNAS_EXCEL, ruta_maestro.name)

    resumen = ResumenTransferencia()
    # Se calcula una sola vez y se incrementa en memoria: volver a escanear la hoja
    # con `primera_fila_libre` en cada inserción es O(n²) sobre miles de filas.
    siguiente_fila_libre = excel_writer.primera_fila_libre(ws_maestro, columna_clave=1)

    for numero_fila, valores in registros:
        if valores.get("ESTADO_VALIDACION") != Veredicto.APROBADO.value:
            resumen.omitidas_no_aprobadas += 1
            continue

        fila = FilaHerramienta.desde_dict_por_columna(valores)
        clave = fila.clave_natural
        ya_marcada_en_planilla = bool(valores.get("TRANSFERIDO_EL"))
        if not clave or ya_marcada_en_planilla or audit_db.ya_transferida(DOMINIO, clave):
            resumen.omitidas_ya_transferidas += 1
            continue

        for columna_excel, valor in enumerate(fila.a_fila_excel(), start=1):
            ws_maestro.cell(row=siguiente_fila_libre, column=columna_excel, value=valor)
        siguiente_fila_libre += 1

        registro = audit_db.registrar_transferencia(DOMINIO, clave, str(ruta_matriz), usuario)
        excel_writer.escribir_valores_fila(
            ws_matriz,
            numero_fila,
            indice_auditoria,
            {"TRANSFERIDO_EL": registro.fecha_hora, "TRANSFERIDO_POR": registro.usuario},
        )
        resumen.transferidas += 1

    excel_writer.guardar(wb_maestro, ruta_maestro)
    excel_writer.guardar(wb_matriz, ruta_matriz)
    return resumen
