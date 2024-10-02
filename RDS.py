import time
import threading
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
#from monitor import Scanning
from processing import Processing
from detection import Detection

class RDS():

    def __init__(self, 
                 vga_gain: int = 0,
                 lna_gain: int = 0,
                 sample_rate: float = 20e6,
                 overlap: int = 0,
                 time_to_read: float = 1,):
        #self.scan = Scanning(vga_gain=vga_gain, lna_gain=lna_gain, sample_rate=sample_rate, overlap=overlap, time_to_read=time_to_read)
        self.pros = Processing()
        self.detec = Detection()
        self.excel_file = 'Hoja de cálculo sin título (1).xlsx'
        """Initialize the RDS object with the given parameters.

        Parameters
        ----------
        vga_gain : int, optional
            Gain for the VGA (default is 0).
        lna_gain : int, optional
            Gain for the LNA (default is 0).
        sample_rate : float, optional
            Sample rate in Hz (default is 20e6).
        overlap : int, optional
            Overlap between frequency steps in Hz (default is 0).
        time_to_read : float, optional
            Duration of time to read samples in seconds (default is 1).
        """

    #def save_to_excel(self, df, sheet_name='Hoja 1'):
        #df = pd.DataFrame([df])  # Convertir el dato en un DataFrame de pandas
        #try:
            #with pd.ExcelWriter(self.excel_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                #df.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=writer.sheets[sheet_name].max_row)
        #except FileNotFoundError:
            #df.to_excel(self.excel_file, sheet_name=sheet_name, index=False)

    def parameter(self, hours_to_scan: int = 1, city: str = 'Manizales'):
        frequencies = self.detec.broadcasters(city)
        parameters_1s = []
        parameters = []
        
        sample_index = np.random.randint(0, 30)
        samples = np.load(f'muestras_guardadas/Samples 88 and 108MHz, time to read 0.01s, sample #{sample_index}.npy')

        f, Pxx = self.pros.welch(samples, fs=20e6)
        f = np.linspace(88, 108, len(Pxx))

        _, _, noise_lvl, _ = self.detec.power_based_detection(f, Pxx)

        for j in range(len(frequencies)):
            f_start, f_end = self.detec.bandwidth(f, Pxx, frequencies[j], noise_lvl)
            bandwidth = f_end - f_start
            index = np.where(np.isclose(f, frequencies[j], atol=0.01))[0]

            parameters.append({
                'time': time.strftime('%X'),
                'freq': round(frequencies[j], 1),
                'bandwidth': round(bandwidth, 2),
                'power': Pxx[index[0]],
                'snr': 10 * np.log10(Pxx[index[0]]/Pxx[0])
            })
        parameters_1s.append(parameters)

        return parameters_1s, f, Pxx

