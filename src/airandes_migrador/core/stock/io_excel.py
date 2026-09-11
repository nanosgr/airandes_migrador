"""Orquesta la lectura del archivo de trabajo del Cargador, la aplicación de los
Módulos A (clasificación) y B (ubicación por defecto), la evaluación del Módulo C
(validación) y la transferencia de las filas aprobadas al maestro `STOCK_CAVOK.xlsx`,
hoja `STOCK`.

Las columnas auxiliares que alimentan el Módulo A/C (familia y nodo contable de
ClaseX, si el artículo es serializado, si su saldo viene negativo) se leen como
columnas OPCIONALES de la propia hoja de trabajo: si el Cargador las incluyó
(por ejemplo copiándolas desde la hoja Trazabilidad_ClaseX del extract de precarga),
se usan; si no están, el Módulo A deja la fila en "General" para revisión humana y el
Módulo C asume que la fila no es serializada / no tiene saldo negativo detectado."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from airandes_migrador.core.common.texto import combinar_observaciones
from airandes_migrador.core.common.validacion import (
    ResultadoValidacion,
    ResumenTransferencia,
    ResumenValidacion,
    Veredicto,
)
from airandes_migrador.core.stock.clasificacion import clasificar_fila
from airandes_migrador.core.stock.config import ConfigStock
from airandes_migrador.core.stock.modelo import NOMBRES_COLUMNAS_EXCEL, FilaStock
from airandes_migrador.core.stock.reglas import evaluar_fila_stock
from airandes_migrador.core.stock.ubicacion import aplicar_ubicacion_por_defecto
from airandes_migrador.core.stock.unidades import homologar_unidad
from airandes_migrador.infra import excel_reader, excel_writer
from airandes_migrador.infra.db import AuditoriaDB
from airandes_migrador.infra.excel_styles import aplicar_fill_fila

HOJA_STOCK = "STOCK"
DOMINIO = "stock"

COLUMNAS_AUDITORIA = ["SEMAFORO", "ESTADO_VALIDACION", "TRANSFERIDO_EL", "TRANSFERIDO_POR"]
COLUMNAS_AUXILIARES_OPCIONALES = [
    "FAMILIA_CLASEX",
    "NODO_CONTABLE_CLASEX",
    "ES_SERIALIZADO",
    "CANTIDAD_NEGATIVA",
]
_VALORES_VERDADEROS = {"SI", "SÍ", "S", "VERDADERO", "TRUE", "1", True, 1}


@dataclass
class FilaEvaluada:
    fila_excel: int
    fila: FilaStock
    resultado: ResultadoValidacion


@dataclass
class ResumenModulosStock:
    ubicaciones_inyectadas: int = 0
    clasificaciones_sin_match: int = 0


def _a_bool(valor: object) -> bool:
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return False
    return str(valor).strip().upper() in {str(v).upper() for v in _VALORES_VERDADEROS}


def leer_filas_trabajo(ruta: Path, hoja: str = HOJA_STOCK) -> list[tuple[int, FilaStock]]:
    _, ws = excel_reader.abrir_hoja(ruta, hoja, solo_lectura=True)
    excel_reader.validar_encabezado(ws, NOMBRES_COLUMNAS_EXCEL, ruta.name)
    columnas_aux = excel_reader.indices_columnas_opcionales(ws, COLUMNAS_AUXILIARES_OPCIONALES)
    registros = excel_reader.leer_filas_como_dicts(
        ws, NOMBRES_COLUMNAS_EXCEL + list(columnas_aux.keys())
    )
    filas = []
    for numero_fila, valores in registros:
        fila = FilaStock.desde_dict_por_columna(valores)
        fila.familia_claseX = valores.get("FAMILIA_CLASEX")
        fila.nodo_contable_claseX = valores.get("NODO_CONTABLE_CLASEX")
        fila.es_serializado = _a_bool(valores.get("ES_SERIALIZADO"))
        fila.cantidad_negativa = _a_bool(valores.get("CANTIDAD_NEGATIVA"))
        filas.append((numero_fila, fila))
    return filas


def generar_matriz_validacion(
    ruta_entrada: Path,
    ruta_salida_matriz: Path,
    config: ConfigStock,
    hoja: str = HOJA_STOCK,
) -> tuple[list[FilaEvaluada], ResumenValidacion, ResumenModulosStock]:
    wb, ws = excel_reader.abrir_hoja(ruta_entrada, hoja, solo_lectura=False)
    excel_reader.validar_encabezado(ws, NOMBRES_COLUMNAS_EXCEL, ruta_entrada.name)
    columnas_aux = excel_reader.indices_columnas_opcionales(ws, COLUMNAS_AUXILIARES_OPCIONALES)
    registros = excel_reader.leer_filas_como_dicts(
        ws, NOMBRES_COLUMNAS_EXCEL + list(columnas_aux.keys())
    )

    indice_auditoria = excel_writer.agregar_columnas_si_faltan(ws, COLUMNAS_AUDITORIA)
    indice_datos = excel_reader.indices_columnas(
        ws, ["CATEGORÍA", "TIPO", "XYZ", "UBICACIÓN", "UNIDAD DE MEDIDA", "OBSERVACIONES"]
    )

    evaluadas: list[FilaEvaluada] = []
    conteos = {Veredicto.APROBADO: 0, Veredicto.PENDIENTE: 0, Veredicto.RECHAZADO: 0}
    modulos = ResumenModulosStock()
    ultima_columna_datos = len(NOMBRES_COLUMNAS_EXCEL)

    for numero_fila, valores in registros:
        fila = FilaStock.desde_dict_por_columna(valores)
        fila.familia_claseX = valores.get("FAMILIA_CLASEX")
        fila.nodo_contable_claseX = valores.get("NODO_CONTABLE_CLASEX")
        fila.es_serializado = _a_bool(valores.get("ES_SERIALIZADO"))
        fila.cantidad_negativa = _a_bool(valores.get("CANTIDAD_NEGATIVA"))

        # Módulo A: solo clasifica si el Cargador no completó ya CATEGORÍA/TIPO/XYZ.
        if not (fila.categoria and fila.tipo and fila.xyz):
            clasificacion = clasificar_fila(
                fila.familia_claseX,
                fila.nodo_contable_claseX,
                config.diccionario_categorias,
                config.matriz_tipo_xyz,
            )
            fila.categoria = fila.categoria or clasificacion.categoria
            fila.tipo = fila.tipo or clasificacion.tipo
            fila.xyz = fila.xyz or clasificacion.xyz
            if clasificacion.requiere_revision_humana:
                modulos.clasificaciones_sin_match += 1
                fila.observaciones = combinar_observaciones(
                    fila.observaciones,
                    "Clasificación automática sin coincidencia: requiere revisión humana",
                )

        # Módulo B: ubicación por defecto.
        if aplicar_ubicacion_por_defecto(fila, config.catalogos.ubicacion_por_defecto):
            modulos.ubicaciones_inyectadas += 1

        # Homologación de unidades.
        fila.unidad = homologar_unidad(fila.unidad, config.catalogos.unidades_homologadas)

        # Módulo C.
        resultado = evaluar_fila_stock(fila, config.catalogos)
        conteos[resultado.veredicto] += 1
        fila.observaciones = combinar_observaciones(
            fila.observaciones, resultado.texto_observaciones()
        )

        ws.cell(row=numero_fila, column=indice_datos["CATEGORÍA"], value=fila.categoria)
        ws.cell(row=numero_fila, column=indice_datos["TIPO"], value=fila.tipo)
        ws.cell(row=numero_fila, column=indice_datos["XYZ"], value=fila.xyz)
        ws.cell(row=numero_fila, column=indice_datos["UBICACIÓN"], value=fila.ubicacion)
        ws.cell(row=numero_fila, column=indice_datos["UNIDAD DE MEDIDA"], value=fila.unidad)
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
    return evaluadas, resumen, modulos


def transferir_aprobadas(
    ruta_matriz: Path,
    ruta_maestro: Path,
    usuario: str,
    audit_db: AuditoriaDB,
    hoja: str = HOJA_STOCK,
) -> ResumenTransferencia:
    columnas_matriz = NOMBRES_COLUMNAS_EXCEL + COLUMNAS_AUDITORIA
    wb_matriz, ws_matriz = excel_reader.abrir_hoja(ruta_matriz, hoja, solo_lectura=False)
    registros = excel_reader.leer_filas_como_dicts(ws_matriz, columnas_matriz)
    indice_auditoria = excel_reader.indices_columnas(ws_matriz, COLUMNAS_AUDITORIA)

    wb_maestro, ws_maestro = excel_reader.abrir_hoja(ruta_maestro, hoja, solo_lectura=False)
    excel_reader.validar_encabezado(ws_maestro, NOMBRES_COLUMNAS_EXCEL, ruta_maestro.name)

    resumen = ResumenTransferencia()
    siguiente_fila_libre = excel_writer.primera_fila_libre(ws_maestro, columna_clave=1)

    for numero_fila, valores in registros:
        if valores.get("ESTADO_VALIDACION") != Veredicto.APROBADO.value:
            resumen.omitidas_no_aprobadas += 1
            continue

        fila = FilaStock.desde_dict_por_columna(valores)
        clave = fila.clave_natural
        ya_marcada_en_planilla = bool(valores.get("TRANSFERIDO_EL"))
        if not clave.strip("|") or ya_marcada_en_planilla or audit_db.ya_transferida(
            DOMINIO, clave
        ):
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
