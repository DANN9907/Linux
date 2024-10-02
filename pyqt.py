import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from RDS import RDS
from pycallgraph import PyCallGraph, Config
from pycallgraph.output import GraphvizOutput
from pycallgraph import GlobbingFilter

class MiVentana(QWidget):
    def __init__(self):
        super().__init__()
        self.rds_instance = RDS()

        self.setWindowTitle('Simulación de Espectro de Radiofrecuencia')
        self.setGeometry(100, 100, 1200, 800)

        layout_principal = QVBoxLayout(self)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.iniciar_actualizacion)
        layout_principal.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.detener_actualizacion)
        layout_principal.addWidget(self.stop_button)

        self.canvas = FigureCanvas(plt.Figure(figsize=(10, 5)))
        layout_principal.addWidget(self.canvas)

        self.table = QTableWidget(9, 4)  # Assuming 9 rows for 9 stations and 4 data columns
        self.table.setHorizontalHeaderLabels(['Frecuencia', 'Bandwidth', 'Max Power', 'SNR'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_principal.addWidget(self.table)

        self.setLayout(layout_principal)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_datos)

    def iniciar_actualizacion(self):
        if not self.timer.isActive():
            self.timer.start(5000)  # Update every 5 seconds

    def detener_actualizacion(self):
        if self.timer.isActive():
            self.timer.stop()

    def actualizar_datos(self):
        parameters_1s, f, Pxx = self.rds_instance.parameter()
        self.generar_grafica(f, Pxx)
        self.actualizar_tabla(parameters_1s[0])  # Assuming parameters_1s is a list of lists of dictionaries

    def generar_grafica(self, f, Pxx):
        self.canvas.figure.clf()
        ax = self.canvas.figure.add_subplot(111)
        ax.semilogy(f, Pxx)
        ax.set_title('Densidad espectral de potencia')
        ax.set_xlabel('Frecuencia (Hz)')
        ax.set_ylabel('PSD (dB/Hz)')
        ax.grid(True)
        self.canvas.draw()

    def actualizar_tabla(self, data):
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            freq_item = QTableWidgetItem(f"{row['freq']:.2f} Hz")
            freq_item.setTextAlignment(Qt.AlignCenter)
            
            bandwidth_item = QTableWidgetItem(f"{row['bandwidth']:.2f} Hz")
            bandwidth_item.setTextAlignment(Qt.AlignCenter)
            
            power_item = QTableWidgetItem(f"{row['power']:.3e} dB/Hz")
            power_item.setTextAlignment(Qt.AlignCenter)
            
            snr_item = QTableWidgetItem(f"{row['snr']:.2f} dB")
            snr_item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(i, 0, freq_item)
            self.table.setItem(i, 1, bandwidth_item)
            self.table.setItem(i, 2, power_item)
            self.table.setItem(i, 3, snr_item)

if __name__ == '__main__':
    config = Config()
    config.trace_filter = GlobbingFilter(include=[
        'MiVentana.*',
        'RDS.*',
        # Añade aquí los módulos o clases que deseas incluir
    ], exclude=[
        'PyQt5.*',
        'matplotlib.*',
        # Añade aquí los módulos que deseas excluir
    ])

    graphviz = GraphvizOutput()
    graphviz.output_file = 'callgraph.png'

    with PyCallGraph(output=graphviz, config=config):
        app = QApplication(sys.argv)
        ventana = MiVentana()
        ventana.show()
        sys.exit(app.exec_())


