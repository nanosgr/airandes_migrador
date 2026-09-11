# Migrador AIRANDES → Cavok

Aplicación de escritorio (Python + PySide6, Windows/Linux) que automatiza los
Módulos de normalización, validación (semáforos) y transferencia descriptos en los
documentos de requerimiento de `../cavok/`, para dos migraciones hacia Cavok:

- **Herramientas Calibradas** (`Import_herramienta.xlsx`, 36 columnas, fuentes GEMA + ClaseX).
- **Stock de Productos** (`STOCK_CAVOK.xlsx`, 20 columnas, fuente ClaseX).

La app **complementa** el flujo de planillas Excel: el Cargador y el Validador
siguen trabajando sobre archivos `.xlsx`/`.xlsm`, y la app ejecuta las reglas de
negocio sobre esos mismos archivos (reemplazando las macros VBA, que solo corren en
Windows con Excel instalado).

## Requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) para gestionar dependencias y el entorno virtual.

## Desarrollo

```bash
uv sync                 # instala dependencias en .venv
uv run pytest -q        # corre la suite de tests (motor de reglas + integración)
uv run airandes-migrador-ui        # abre la interfaz gráfica
uv run airandes-migrador --help    # modo batch sin interfaz (ver comandos abajo)
```

## Configuración (`config/*.yaml`)

Los catálogos y diccionarios de mapeo son editables a mano, sin recompilar nada:

- `catalogos_herramientas.yaml` — desplegables (SEDE, BASE, UNIDAD, UBICACIÓN,
  ESTADO, EMPRESA CALIBRADORA), campos obligatorios, `INTERVALO_DÍAS`/`ALERTA_DÍAS`.
- `fabricantes_alias.yaml` — normalización de FABRICANTE (Regla 3 de Herramientas).
- `catalogos_stock.yaml` — campos obligatorios (lista completa del SRS 2.3),
  ubicación por defecto, homologación de unidades, monedas válidas.
- `diccionario_categorias.yaml` / `matriz_tipo_xyz.yaml` — mapeo Familia/Nodo
  contable → CATEGORÍA/TIPO/XYZ (Módulo A de Stock). **Las entradas de fábrica son
  solo ejemplos ilustrativos** — hay que completarlas con la tabla oficial que el
  área técnica apruebe (ver PASO 1 de la Metodología de Stock).

En modo desarrollo la app encuentra `config/` automáticamente (es hermana de `src/`).
Para apuntar a otra ubicación (o en un ejecutable empaquetado que no la encuentre),
definí la variable de entorno `AIRANDES_CONFIG_DIR`.

## Uso de la interfaz gráfica

1. Elegir el módulo (Herramientas o Stock) desde la pantalla de inicio.
2. Seleccionar el archivo de trabajo (por ejemplo, los extracts de precarga
   `Import_herramienta_PRECARGA.xlsx` / `STOCK_CAVOK_PRECARGA.xlsx` del directorio
   del proyecto, o `01_Trabajo_Calibradas.xlsx` / `01_Stock_PreCarga_Trabajo.xlsx`).
3. "Validar": aplica los Módulos A/B/C, escribe semáforo/observaciones/colores en el
   propio archivo y muestra la tabla de revisión (filtrable por ROJO/NARANJA/VERDE).
4. Seleccionar el archivo maestro destino (`Import_herramienta.xlsx` / `STOCK_CAVOK.xlsx`).
5. "Transferir filas APROBADO": copia al maestro solo las filas aprobadas que no
   fueron transferidas antes (operación idempotente — correrla de nuevo no duplica).

El nombre del operador se pide una sola vez (menú *Navegación → Cambiar operador*) y
queda registrado en las columnas de auditoría de cada transferencia.

## Modo batch (CLI, sin interfaz)

```bash
uv run airandes-migrador validar-herramientas 01_Trabajo_Calibradas.xlsx
uv run airandes-migrador transferir-herramientas 01_Trabajo_Calibradas.xlsx Import_herramienta.xlsx --usuario "Brian V."

uv run airandes-migrador validar-stock 01_Stock_PreCarga_Trabajo.xlsx
uv run airandes-migrador transferir-stock 01_Stock_PreCarga_Trabajo.xlsx STOCK_CAVOK.xlsx --usuario "Nico Rinaudo"
```

## Empaquetado (ejecutable standalone)

PyInstaller no cross-compila: el build de Windows debe correr en Windows, y el de
Linux en Linux.

```bash
uv run pyinstaller packaging/pyinstaller_linux.spec     # o pyinstaller_windows.spec en Windows
```

Genera `dist/airandes-migrador/`. Copiar esa carpeta junto con `config/` al equipo
destino (el ejecutable busca `config/` junto a sí mismo). Para instalar en un equipo
sin `uv`/Python, distribuir esa carpeta completa; no requiere Excel instalado.

## Datos persistentes de la app

- Base de auditoría/idempotencia (SQLite): `%APPDATA%\airandes_migrador\auditoria.db`
  en Windows, `~/.local/share/airandes_migrador/auditoria.db` en Linux. Override con
  la variable de entorno `AIRANDES_DATA_DIR`.
- Nombre del operador y preferencias: `QSettings` (registro de Windows / archivo de
  configuración de Linux, bajo `AIRANDES / Migrador Cavok`).

## Estructura del proyecto

```
config/                  catálogos YAML editables
src/airandes_migrador/
  core/                   lógica de negocio pura (testeable sin PySide6)
    common/               tipos y utilidades compartidas (Semaforo, ResultadoValidacion, ...)
    herramientas/         modelo, reglas, normalización, I/O Excel del módulo Herramientas
    stock/                modelo, reglas, clasificación, ubicación, unidades, I/O Excel de Stock
  infra/                  adaptadores técnicos: lectura/escritura Excel, estilos, SQLite
  ui/                     PySide6 (sin lógica de negocio propia)
  cli.py                  modo batch
  app.py                  punto de entrada de la interfaz gráfica
tests/                    pytest: motor de reglas + integración end-to-end
packaging/                specs de PyInstaller
```
