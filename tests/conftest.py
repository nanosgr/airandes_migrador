from __future__ import annotations

from datetime import date

import pytest

from airandes_migrador.core.herramientas.config import CatalogosHerramientas, FabricantesAlias
from airandes_migrador.core.herramientas.modelo import FilaHerramienta
from airandes_migrador.core.stock.config import CatalogosStock, DiccionarioClasificacion


@pytest.fixture
def catalogos_herramientas() -> CatalogosHerramientas:
    return CatalogosHerramientas(
        sede="AIRANDES",
        bases=["San Fernando", "Córdoba"],
        unidades=["UND", "M", "KG", "SET"],
        ubicaciones=["HANGAR N°1", "LABORATORIO DE PINTURA"],
        estados=["Calibrada", "Disponible", "No disponible", "En reparación"],
        empresas_calibradoras=["JET SERVICE", "CEMEC"],
        campos_obligatorios=["sede", "base", "nombre", "sn", "unidad", "ubicacion"],
        intervalo_dias_default=365,
        alerta_dias_default=30,
        estados_vencida_bloqueantes=["Calibrada", "Disponible"],
        estados_vencida_pendientes=["No disponible", "En reparación"],
    )


@pytest.fixture
def fabricantes_alias() -> FabricantesAlias:
    return FabricantesAlias(
        alias={
            "CONSOLIDATED DEVICES INC": "CONSOLIDATED DEVICES INC (CDI)",
            "CDI": "CONSOLIDATED DEVICES INC (CDI)",
            "CONSOLIDATED": "CONSOLIDATED DEVICES INC (CDI)",
            "BRITOOL": "BRITOOL",
            "BRISTOOL": "BRITOOL",
            "AC DELCO": "AC DELCO",
            "DELCO": "AC DELCO",
        }
    )


@pytest.fixture
def fila_herramienta_valida() -> FilaHerramienta:
    def _builder(**overrides) -> FilaHerramienta:
        base = dict(
            sede="AIRANDES",
            base="San Fernando",
            nombre="TORQUIMETRO",
            sn="E045727",
            unidad="UND",
            ubicacion="HANGAR N°1",
            estado="Calibrada",
            ultima_calibracion=date(2026, 1, 1),
            intervalo_dias=365,
            fabricante="BRITOOL",
        )
        base.update(overrides)
        return FilaHerramienta(**base)

    return _builder


@pytest.fixture
def catalogos_stock() -> CatalogosStock:
    return CatalogosStock(
        campos_obligatorios=[
            "nombre",
            "categoria",
            "tipo",
            "xyz",
            "deposito",
            "ubicacion",
            "cantidad",
            "unidad",
            "moneda",
        ],
        ubicacion_por_defecto="POR UBICAR",
        unidades_homologadas={"UNID.": "UND", "METROS": "MT"},
        unidades_validas=["UND", "MT", "KG", "IN2"],
        monedas_validas=["USD", "ARS", "EUR"],
    )


@pytest.fixture
def diccionario_categorias() -> DiccionarioClasificacion:
    return DiccionarioClasificacion(
        reglas=[
            {"campo": "familia", "valor": "HERRAMIENTAS", "categoria": "Herramientas"},
            {"campo": "nodo_contable", "valor": "CONSUMIBLES", "categoria": "Consumibles"},
        ]
    )


@pytest.fixture
def matriz_tipo_xyz() -> DiccionarioClasificacion:
    return DiccionarioClasificacion(
        reglas=[
            {"campo": "nodo_contable", "valor": "COMPONENTES", "tipo": "00", "xyz": "X"},
            {"campo": "nodo_contable", "valor": "CONSUMIBLES", "tipo": "07", "xyz": "Z"},
        ]
    )


@pytest.fixture
def fila_stock_valida():
    from airandes_migrador.core.stock.modelo import FilaStock

    def _builder(**overrides) -> FilaStock:
        base = dict(
            nombre="TORNILLO AN3-4A",
            categoria="Consumibles",
            tipo="07",
            xyz="Z",
            deposito="DEPOSITO CENTRAL",
            ubicacion="ESTANTE A1",
            cantidad=10.0,
            unidad="UND",
            moneda="USD",
            es_serializado=False,
            cantidad_negativa=False,
        )
        base.update(overrides)
        return FilaStock(**base)

    return _builder
