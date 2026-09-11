from __future__ import annotations

from airandes_migrador.core.stock.clasificacion import clasificar_fila


def test_familia_herramientas_matchea_categoria(diccionario_categorias, matriz_tipo_xyz):
    resultado = clasificar_fila("HERRAMIENTAS", None, diccionario_categorias, matriz_tipo_xyz)
    assert resultado.categoria == "Herramientas"


def test_nodo_contable_consumibles_matchea_tipo_y_xyz(diccionario_categorias, matriz_tipo_xyz):
    resultado = clasificar_fila(None, "CONSUMIBLES", diccionario_categorias, matriz_tipo_xyz)
    assert resultado.categoria == "Consumibles"
    assert resultado.tipo == "07"
    assert resultado.xyz == "Z"
    assert not resultado.requiere_revision_humana


def test_comparacion_ignora_mayusculas_y_espacios(diccionario_categorias, matriz_tipo_xyz):
    resultado = clasificar_fila("  herramientas  ", None, diccionario_categorias, matriz_tipo_xyz)
    assert resultado.categoria == "Herramientas"


def test_sin_match_cae_en_general_con_bandera(diccionario_categorias, matriz_tipo_xyz):
    resultado = clasificar_fila("ALGO_DESCONOCIDO", "OTRO", diccionario_categorias, matriz_tipo_xyz)
    assert resultado.categoria == "General"
    assert resultado.requiere_revision_humana


def test_match_parcial_categoria_sin_tipo_xyz_tambien_marca_revision(
    diccionario_categorias, matriz_tipo_xyz
):
    # "HERRAMIENTAS" matchea categoría pero no está en matriz_tipo_xyz del fixture.
    resultado = clasificar_fila("HERRAMIENTAS", None, diccionario_categorias, matriz_tipo_xyz)
    assert resultado.categoria == "Herramientas"
    assert resultado.tipo is None
    assert resultado.requiere_revision_humana
