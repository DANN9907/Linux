import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QTextEdit)
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from RDS import RDS

class MiVentana(QWidget):
    def _init_(self):
        super()._init_()

        rds = RDS()

        # Configuración de la ventana principal
        self.setWindowTitle('Simulación de Espectro de Radiofrecuencia')
        self.setGeometry(100, 100, 1200, 800)  # Ancho de 1200, altura de 800

        # Parámetros fijos
        self.rango_inicial_val = 88
        self.rango_final_val = 108
        self.overlap_val = 0

        # Layout principal que organiza todos los elementos
        layout_principal = QVBoxLayout()

        # Grupo para mostrar los parámetros fijos
        parametros_group = QGroupBox("Parámetros de Entrada")
        layout_parametros = QFormLayout()

        # Mostrar parámetros fijos usando etiquetas (QLabel)
        self.rango_inicial_label = QLabel(f'Rango inicial (R-I): {self.rango_inicial_val}')
        layout_parametros.addRow(self.rango_inicial_label)

        self.rango_final_label = QLabel(f'Rango final (R-F): {self.rango_final_val}')
        layout_parametros.addRow(self.rango_final_label)

        self.overlap_label = QLabel(f'Overlap (O): {self.overlap_val}')
        layout_parametros.addRow(self.overlap_label)

        parametros_group.setLayout(layout_parametros)
        layout_principal.addWidget(parametros_group)

        # Botón "Start" para iniciar la actualización automática de la gráfica
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.iniciar_actualizacion)
        layout_principal.addWidget(self.start_button)

        # Botón "Stop" para detener la actualización automática de la gráfica
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.detener_actualizacion)
        layout_principal.addWidget(self.stop_button)

        # Área de resultados que contiene la gráfica y los datos adicionales
        resultados_group = QGroupBox("Resultados")
        layout_resultados = QVBoxLayout()

        # Integrar la gráfica de Matplotlib en la interfaz
        self.canvas = FigureCanvas(plt.Figure(figsize=(13, 5)))
        layout_resultados.addWidget(self.canvas)

        # Cuadro de texto para mostrar información adicional sobre los datos
        self.texto_resultados = QTextEdit()
        self.texto_resultados.setPlaceholderText("Aquí se mostrarán los datos como Bandwidth, Separation, SNR, Max Power...")
        self.texto_resultados.setReadOnly(True)
        layout_resultados.addWidget(self.texto_resultados)

        resultados_group.setLayout(layout_resultados)
        layout_principal.addWidget(resultados_group)

        # Configurar el layout principal de la ventana
        self.setLayout(layout_principal)

        # Temporizador para la actualización automática de la gráfica
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_grafica)

    def iniciar_actualizacion(self):
        print("Start presionado")  # Mensaje de depuración
        # Solo iniciar el temporizador si no está activo
        if not self.timer.isActive():
            self.timer.start(5000)  # Temporizador configurado para 30 segundos
            print("Temporizador iniciado para actualizar cada 30 segundos")  # Mensaje de depuración
        # Llama a actualizar_grafica para mostrar la gráfica inmediatamente
        self.actualizar_grafica()

    def detener_actualizacion(self):
        print("Stop presionado")  # Mensaje de depuración
        if self.timer.isActive():
            self.timer.stop()
            print("Temporizador detenido")  # Mensaje de depuración

    def actualizar_grafica(self):
        print("Actualizando gráfica...")  # Mensaje de depuración
        self.generar_grafica()

        # Generar datos aleatorios para los resultados adicionales
        bandwidth = np.random.uniform(100, 300)  # Ancho de banda aleatorio (entre 100 y 300 Hz)
        separation = np.random.uniform(5, 20)  # Separación aleatoria (entre 5 y 20 unidades)
        snr = np.random.uniform(10, 40)  # Relación señal-ruido aleatoria (entre 10 y 40 dB)
        max_power = np.random.uniform(10, 100)  # Potencia máxima aleatoria (entre 10 y 100 W)

        # Mostrar datos calculados en el cuadro de texto
        self.texto_resultados.setText(f"""
        Datos calculados:
        - Bandwidth: {bandwidth:.2f} Hz
        - Separation: {separation:.2f} units
        - Signal Noise Relation (SNR): {snr:.2f} dB
        - Max Power: {max_power:.2f} W
        """)

    def generar_grafica(self):
        print("Generando nueva gráfica...")  # Mensaje de depuración

        # Limpiar cualquier contenido anterior en la gráfica
        self.canvas.figure.clf()

        # Crear una nueva gráfica en la figura del canvas
        ax = self.canvas.figure.add_subplot(111)

        # Generar datos aleatorios para la gráfica
        x_values = np.linspace(0, 10, 100)  # Vector de 100 puntos para el eje x (0 a 10)
        y_values = np.random.normal(0, 1, 100)  # Vector de datos aleatorios para el eje y (distribución normal)

        # Imprimir los datos generados para depuración
        print("Datos de la gráfica (x):", x_values)
        print("Datos de la gráfica (y):", y_values)

        # Dibujar la gráfica con los datos generados
        ax.plot(x_values, y_values, label='Datos Aleatorios')
        ax.set_xlabel('Tiempo (s)')  # Etiqueta del eje x
        ax.set_ylabel('Amplitud')  # Etiqueta del eje y
        ax.set_title('Señal de Datos Aleatorios Actualizada')  # Título de la gráfica
        ax.grid(True)  # Añadir cuadrícula a la gráfica
        ax.legend()  # Añadir leyenda a la gráfica

        # Actualizar el canvas para que la gráfica sea visible
        self.canvas.draw()

if _name_ == '_main_':
    # Crear la aplicación de PyQt5
    app = QApplication(sys.argv)

    # Crear y mostrar la ventana principal
    ventana = MiVentana()
    ventana.show()

    # Ejecutar la aplicación
    sys.exit(app.exec_())