"""Vista del módulo Herramientas Calibradas: seleccionar el archivo de trabajo,
ejecutar las Reglas 1/2/3, revisar la tabla con semáforo y transferir las filas
APROBADO al maestro `Import_herramienta.xlsx`.

Es el flujo de referencia: `ui/stock/vista.py` reutiliza los mismos componentes de
`ui/common/` con la misma estructura."""

from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from airandes_migrador.config_paths import directorio_config_por_defecto, directorio_datos_app
from airandes_migrador.core.common.validacion import Semaforo
from airandes_migrador.core.herramientas import io_excel
from airandes_migrador.core.herramientas.config import cargar_config_herramientas
from airandes_migrador.infra.db import AuditoriaDB
from airandes_migrador.ui.common.file_picker import SelectorArchivo
from airandes_migrador.ui.common.filtro_semaforo import ProxyFiltroSemaforo
from airandes_migrador.ui.common.log_panel import PanelLog
from airandes_migrador.ui.common.operador import obtener_operador
from airandes_migrador.ui.common.tabla_model import ModeloTablaEvaluacion
from airandes_migrador.ui.common.worker import TareaEnHilo

_COLUMNAS_TABLA = [
    ("SN", lambda fe: fe.fila.sn),
    ("NOMBRE", lambda fe: fe.fila.nombre),
    ("FABRICANTE", lambda fe: fe.fila.fabricante),
    ("ESTADO", lambda fe: fe.fila.estado),
    ("ÚLTIMA CALIBRACIÓN", lambda fe: fe.fila.ultima_calibracion),
    ("SEMÁFORO", lambda fe: fe.resultado.semaforo.value),
    ("VEREDICTO", lambda fe: fe.resultado.veredicto.value),
    ("OBSERVACIONES", lambda fe: fe.resultado.texto_observaciones()),
]

_OPCIONES_FILTRO = [
    ("Todas", None),
    ("Solo ROJO", Semaforo.ROJO),
    ("Solo NARANJA", Semaforo.NARANJA),
    ("Solo VERDE", Semaforo.VERDE),
]


class VistaHerramientas(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._audit_db = AuditoriaDB(directorio_datos_app() / "auditoria.db")
        self._hilo: TareaEnHilo | None = None

        layout = QVBoxLayout(self)

        titulo = QLabel("<h2>Herramientas Calibradas</h2>")
        layout.addWidget(titulo)

        grupo_entrada = QGroupBox("1. Archivo de trabajo (Cargador)")
        layout_entrada = QVBoxLayout(grupo_entrada)
        self._selector_entrada = SelectorArchivo(
            "Elegir archivo de trabajo (01_Trabajo_Calibradas o extract de precarga)"
        )
        layout_entrada.addWidget(self._selector_entrada)
        fila_botones = QHBoxLayout()
        self._boton_validar = QPushButton("Validar (Reglas 1/2/3)")
        self._boton_validar.clicked.connect(self._on_validar)
        fila_botones.addWidget(self._boton_validar)
        fila_botones.addStretch(1)
        layout_entrada.addLayout(fila_botones)
        layout.addWidget(grupo_entrada)

        grupo_resultados = QGroupBox("2. Resultados de validación")
        layout_resultados = QVBoxLayout(grupo_resultados)
        fila_resumen = QHBoxLayout()
        self._etiqueta_resumen = QLabel("Sin validar todavía.")
        fila_resumen.addWidget(self._etiqueta_resumen, stretch=1)
        fila_resumen.addWidget(QLabel("Filtro:"))
        self._combo_filtro = QComboBox()
        for texto, _ in _OPCIONES_FILTRO:
            self._combo_filtro.addItem(texto)
        self._combo_filtro.currentIndexChanged.connect(self._on_cambiar_filtro)
        fila_resumen.addWidget(self._combo_filtro)
        layout_resultados.addLayout(fila_resumen)

        self._modelo_tabla = ModeloTablaEvaluacion(_COLUMNAS_TABLA)
        self._proxy = ProxyFiltroSemaforo()
        self._proxy.setSourceModel(self._modelo_tabla)
        self._tabla = QTableView()
        self._tabla.setModel(self._proxy)
        self._tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._tabla.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._tabla.setAlternatingRowColors(False)
        layout_resultados.addWidget(self._tabla)
        layout.addWidget(grupo_resultados, stretch=1)

        grupo_transferencia = QGroupBox("3. Transferir aprobadas al maestro")
        layout_transferencia = QVBoxLayout(grupo_transferencia)
        self._selector_maestro = SelectorArchivo("Elegir Import_herramienta.xlsx (maestro)")
        layout_transferencia.addWidget(self._selector_maestro)
        fila_botones_transf = QHBoxLayout()
        self._boton_transferir = QPushButton("Transferir filas APROBADO")
        self._boton_transferir.clicked.connect(self._on_transferir)
        fila_botones_transf.addWidget(self._boton_transferir)
        fila_botones_transf.addStretch(1)
        layout_transferencia.addLayout(fila_botones_transf)
        layout.addWidget(grupo_transferencia)

        self._log = PanelLog()
        self._log.setMaximumHeight(140)
        layout.addWidget(QLabel("Registro:"))
        layout.addWidget(self._log)

    def _set_botones_habilitados(self, habilitado: bool) -> None:
        self._boton_validar.setEnabled(habilitado)
        self._boton_transferir.setEnabled(habilitado)

    def _on_cambiar_filtro(self, indice: int) -> None:
        _, semaforo = _OPCIONES_FILTRO[indice]
        self._proxy.set_filtro_semaforo(semaforo)

    def _on_validar(self) -> None:
        ruta_entrada = self._selector_entrada.ruta()
        if ruta_entrada is None:
            QMessageBox.warning(self, "Falta archivo", "Elegí primero el archivo de trabajo.")
            return

        self._log.info(f"Validando '{ruta_entrada.name}'…")
        self._set_botones_habilitados(False)

        def tarea() -> tuple:
            config = cargar_config_herramientas(directorio_config_por_defecto())
            return io_excel.generar_matriz_validacion(
                ruta_entrada, ruta_entrada, config, date.today()
            )

        self._hilo = TareaEnHilo(tarea)
        self._hilo.completada.connect(self._on_validacion_completa)
        self._hilo.fallo.connect(self._on_error)
        self._hilo.start()

    def _on_validacion_completa(self, resultado: tuple) -> None:
        evaluadas, resumen = resultado
        self._modelo_tabla.actualizar_filas(evaluadas)
        self._etiqueta_resumen.setText(
            f"Total: {resumen.total}  |  Aprobadas: {resumen.aprobadas}  |  "
            f"Pendientes: {resumen.pendientes}  |  Rechazadas: {resumen.rechazadas}"
        )
        self._log.info(
            f"Validación completa: {resumen.aprobadas} aprobadas, "
            f"{resumen.pendientes} pendientes, {resumen.rechazadas} rechazadas."
        )
        self._set_botones_habilitados(True)

    def _on_transferir(self) -> None:
        ruta_entrada = self._selector_entrada.ruta()
        ruta_maestro = self._selector_maestro.ruta()
        if ruta_entrada is None or ruta_maestro is None:
            QMessageBox.warning(
                self, "Falta archivo", "Elegí el archivo de trabajo y el maestro destino."
            )
            return
        if self._modelo_tabla.rowCount() == 0:
            QMessageBox.warning(self, "Sin validar", "Ejecutá primero la validación.")
            return

        usuario = obtener_operador(self)
        respuesta = QMessageBox.question(
            self,
            "Confirmar transferencia",
            f"Se transferirán al maestro las filas con veredicto APROBADO.\n"
            f"Operador registrado: {usuario}\n\n¿Continuar?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        self._log.info(f"Transfiriendo filas aprobadas a '{ruta_maestro.name}'…")
        self._set_botones_habilitados(False)

        def tarea():
            return io_excel.transferir_aprobadas(
                ruta_entrada, ruta_maestro, usuario=usuario, audit_db=self._audit_db
            )

        self._hilo = TareaEnHilo(tarea)
        self._hilo.completada.connect(self._on_transferencia_completa)
        self._hilo.fallo.connect(self._on_error)
        self._hilo.start()

    def _on_transferencia_completa(self, resumen) -> None:
        self._log.info(
            f"Transferencia completa: {resumen.transferidas} transferidas, "
            f"{resumen.omitidas_ya_transferidas} ya transferidas antes, "
            f"{resumen.omitidas_no_aprobadas} no aprobadas."
        )
        self._set_botones_habilitados(True)
        # Revalida para reflejar en la tabla las columnas TRANSFERIDO_EL/POR ya escritas.
        self._on_validar()

    def _on_error(self, mensaje: str) -> None:
        self._log.error(mensaje)
        QMessageBox.critical(self, "Error", mensaje)
        self._set_botones_habilitados(True)
