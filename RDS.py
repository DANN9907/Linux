import time
import numpy as np
import pandas as pd 
from monitor import Scanning
from processing import Processing
from detection import Detection
from hackrf import HackRF

class RDS():

    def __init__(self,
                 city: str = 'Manizales',
                 vga_gain: int = 0,
                 lna_gain: int = 0,
                 sample_rate: float = 20e6,
                 overlap: int = 0,
                 time_to_read: float = 1, 
                 ):
        # self.scan = Scanning(vga_gain=vga_gain, lna_gain=lna_gain, sample_rate=sample_rate, overlap=overlap, time_to_read=time_to_read)
        self.pros = Processing()
        self.detec = Detection()
        self.frequencies = self.detec.broadcasters(city)
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

    def parameter(self, iter):
        """The bandwidth and maximum power parameters of each radio station are calculated every second. 
        Every 5 minutes, all the obtained parameters are averaged, and at the end of the analysis hours, 
        the averages are averaged again.

        Parameters
        ----------
        hours_to_scan : int
            Total hours to analyze
        city : str
            

        Returns
        -------
        parameters_prom_12h_final: dictionarie contains:
        - 'freq': float : Frequencies for each broadcaster.
        - 'bandwidth' : Bandwidth for each broadcaster.
        - 'power' : power in central frequency for each broadcaster.

        parameters_prom_12h: dictionarie of list contains:
        - 'freq': float : Frequencies for each broadcaster.
        - 'bandwidth' : Bandwidth for each broadcaster.
        - 'power' : power in central frequency for each broadcaster.
        """
        
        parameters_1s = []
        parameters = []

        samples = np.load(f'/home/dann99/Documentos/GitHub/python-gcpds.em_spectrum_monitor/database_prueba_piloto/Samples 88 and 108MHz, time to read 0.01s, sample #0.npy')

        f, Pxx = self.pros.welch(samples, fs=20e6)
        f = np.linspace(88, 108, len(Pxx))
        
        noise_lvl = self.detec.power_based_detection(f, Pxx)  

        for j in range(len(self.frequencies)):

            f_start, f_end = self.detec.bandwidth(f, Pxx, self.frequencies[j], noise_lvl)
            bandwidth = f_end - f_start

            index = np.where(np.isclose(f, self.frequencies[j], atol=0.01))[0]

            parameters.append({
                        'time': time.strftime('%X'),
                        'freq': round(self.frequencies[j], 1),
                        'bandwidth': round(bandwidth, 2),
                        'power': 10 * np.log10(Pxx[index[0]]),
                        'snr': 10 * np.log10(Pxx[index[0]]/Pxx[0])
                    })
        parameters_1s.append(parameters)

        return parameters_1s, f, Pxx