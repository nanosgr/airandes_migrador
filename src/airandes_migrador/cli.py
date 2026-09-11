"""Modo batch sin interfaz gráfica: corre los mismos Módulos A/B/C que la UI, para
pruebas end-to-end rápidas y como plan B operativo si la GUI no está disponible.

Ejemplos:
    airandes-migrador validar-herramientas 01_Trabajo_Calibradas.xlsx
    airandes-migrador transferir-herramientas 01_Trabajo_Calibradas.xlsx Import_herramienta.xlsx --usuario "Brian V."
    airandes-migrador validar-stock 01_Stock_PreCarga_Trabajo.xlsx
    airandes-migrador transferir-stock 01_Stock_PreCarga_Trabajo.xlsx STOCK_CAVOK.xlsx --usuario "Nico Rinaudo"
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from airandes_migrador.config_paths import directorio_config_por_defecto, directorio_datos_app
from airandes_migrador.core.herramientas import io_excel as herramientas_io
from airandes_migrador.core.herramientas.config import cargar_config_herramientas
from airandes_migrador.core.stock import io_excel as stock_io
from airandes_migrador.core.stock.config import cargar_config_stock
from airandes_migrador.infra.db import AuditoriaDB


def _agregar_argumento_config(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config", type=Path, default=None, help="Carpeta config/ (por defecto, autodetectada)"
    )


def _resolver_config(args: argparse.Namespace) -> Path:
    return args.config or directorio_config_por_defecto()


def cmd_validar_herramientas(args: argparse.Namespace) -> None:
    config = cargar_config_herramientas(_resolver_config(args))
    salida = args.salida or args.entrada
    evaluadas, resumen = herramientas_io.generar_matriz_validacion(
        args.entrada, salida, config, date.today()
    )
    print(f"Total: {resumen.total}  Aprobadas: {resumen.aprobadas}  "
          f"Pendientes: {resumen.pendientes}  Rechazadas: {resumen.rechazadas}")
    print(f"Matriz de validación escrita en: {salida}")


def cmd_transferir_herramientas(args: argparse.Namespace) -> None:
    audit_db = AuditoriaDB(args.db or directorio_datos_app() / "auditoria.db")
    resumen = herramientas_io.transferir_aprobadas(
        args.matriz, args.maestro, usuario=args.usuario, audit_db=audit_db
    )
    print(
        f"Transferidas: {resumen.transferidas}  "
        f"Ya transferidas antes: {resumen.omitidas_ya_transferidas}  "
        f"No aprobadas: {resumen.omitidas_no_aprobadas}"
    )


def cmd_validar_stock(args: argparse.Namespace) -> None:
    config = cargar_config_stock(_resolver_config(args))
    salida = args.salida or args.entrada
    evaluadas, resumen, modulos = stock_io.generar_matriz_validacion(args.entrada, salida, config)
    print(f"Total: {resumen.total}  Aprobadas: {resumen.aprobadas}  "
          f"Pendientes: {resumen.pendientes}  Rechazadas: {resumen.rechazadas}")
    print(f"Ubicaciones inyectadas por defecto: {modulos.ubicaciones_inyectadas}")
    print(f"Clasificaciones sin match (quedaron 'General'): {modulos.clasificaciones_sin_match}")
    print(f"Matriz de validación escrita en: {salida}")


def cmd_transferir_stock(args: argparse.Namespace) -> None:
    audit_db = AuditoriaDB(args.db or directorio_datos_app() / "auditoria.db")
    resumen = stock_io.transferir_aprobadas(
        args.matriz, args.maestro, usuario=args.usuario, audit_db=audit_db
    )
    print(
        f"Transferidas: {resumen.transferidas}  "
        f"Ya transferidas antes: {resumen.omitidas_ya_transferidas}  "
        f"No aprobadas: {resumen.omitidas_no_aprobadas}"
    )


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="airandes-migrador")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_vh = subparsers.add_parser(
        "validar-herramientas", help="Ejecuta Reglas 1/2/3 sobre el archivo de trabajo"
    )
    p_vh.add_argument("entrada", type=Path)
    p_vh.add_argument("--salida", type=Path, default=None)
    _agregar_argumento_config(p_vh)
    p_vh.set_defaults(func=cmd_validar_herramientas)

    p_th = subparsers.add_parser(
        "transferir-herramientas", help="Transfiere filas APROBADO al maestro"
    )
    p_th.add_argument("matriz", type=Path)
    p_th.add_argument("maestro", type=Path)
    p_th.add_argument("--usuario", required=True)
    p_th.add_argument("--db", type=Path, default=None)
    p_th.set_defaults(func=cmd_transferir_herramientas)

    p_vs = subparsers.add_parser(
        "validar-stock", help="Ejecuta Módulos A/B/C sobre el archivo de trabajo"
    )
    p_vs.add_argument("entrada", type=Path)
    p_vs.add_argument("--salida", type=Path, default=None)
    _agregar_argumento_config(p_vs)
    p_vs.set_defaults(func=cmd_validar_stock)

    p_ts = subparsers.add_parser("transferir-stock", help="Transfiere filas APROBADO al maestro")
    p_ts.add_argument("matriz", type=Path)
    p_ts.add_argument("maestro", type=Path)
    p_ts.add_argument("--usuario", required=True)
    p_ts.add_argument("--db", type=Path, default=None)
    p_ts.set_defaults(func=cmd_transferir_stock)

    return parser


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
