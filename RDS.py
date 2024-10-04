import time
import numpy as np
from monitor import Scanning
from processing import Processing
from detection import Detection

class RDS():

    def __init__(self, 
                 vga_gain: int = 0,
                 lna_gain: int = 0,
                 sample_rate: float = 20e6,
                 overlap: int = 0,
                 time_to_read: float = 1,):
        # self.scan = Scanning(vga_gain=vga_gain, lna_gain=lna_gain, sample_rate=sample_rate, overlap=overlap, time_to_read=time_to_read)
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
        
    def parameter(self, city: str = 'Manizales'):
        frequencies = self.detec.broadcasters(city)
        parameters_1s = []
        parameters = []
        bandwidth_list = []

        # wide_samples = self.scan.scan(88e6, 108e6)
        # samples = self.scan.scan(wide_samples, 'mean')
        
        sample_index = np.random.randint(0, 30)
        samples = np.load(f'muestras_guardadas/Samples 88 and 108MHz, time to read 0.01s, sample #{sample_index}.npy')

        f, Pxx = self.pros.welch(samples, fs=20e6)
        f = np.linspace(88, 108, len(Pxx))

        _, _, _, noise_lvl = self.detec.power_based_detection(f, Pxx)

        for j in range(len(frequencies)):
            f_start, f_end = self.detec.bandwidth(f, Pxx, frequencies[j], noise_lvl)
            bandwidth = f_end - f_start
            bandwidth_list.append(f_start)
            bandwidth_list.append(f_end)
            index = np.where(np.isclose(f, frequencies[j], atol=0.01))[0]

            parameters.append({
                'time': time.strftime('%X'),
                'freq': round(frequencies[j], 1),
                'bandwidth': round(bandwidth, 2),
                'power': Pxx[index[0]],
                'snr': 10 * np.log10(Pxx[index[0]]/Pxx[0])
            })
        parameters_1s.append(parameters)

        return parameters_1s, f, Pxx, bandwidth_list

