import numpy as np
import pandas as pd
from scipy.signal import find_peaks

class Detection:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.excel_file = 'Hoja de cálculo sin título (1).xlsx'

    def broadcasters(self, town: str = 'Manizales'):
        """The frequencies where there are radio stations are extracted according to the selected city.

        Parameters
        ----------
        town : string
            Town to extract broadcasters

        Returns
        -------
        NONE
        """
        df = pd.read_csv('Radioemisoras Colombia - Radioemisoras 2023.csv')

        datos_filtrados = df[(df['Municipio'].str.upper() == town.upper()) & 
                                (df['Tecnología transmisión'] == 'FM')]
    
        frequencies = datos_filtrados['Frecuencia'].str.replace(' MHz', '', regex=False).astype(float)
        frequencies = sorted(frequencies)

        return frequencies

    # ----------------------------------------------------------------------
    def power_based_detection(self, f: np.ndarray, Pxx: np.ndarray):
        """
        Detects the presence of peaks in the power spectrum.

        Parameters
        ----------
        f : numpy.ndarray
            The frequencies corresponding to the power spectral density values.
        Pxx : numpy.ndarray
            The power spectral density values.

        Returns
        -------
        peak_freqs : numpy.ndarray
            The frequencies of the detected peaks.
        peak_powers : numpy.ndarray
            The powers of the detected peaks.
        detections : list
            A list with the frequency and power pairs.
        threshold : float
            A floating-point number representing the decision threshold.
        """

        noise_lvl = np.percentile(Pxx, 80)

        signal_level = np.percentile(Pxx, 90)

        threshold = (noise_lvl + signal_level) / 1.5 + 0.4 * ((noise_lvl + signal_level) / 1.5)
        
        peaks, properties = find_peaks(Pxx, height=threshold, distance=50)

        peak_powers = properties['peak_heights']
        peak_freqs = f[peaks]

        # detections = [(freq, power) for freq, power in zip(peak_freqs, peak_powers)]

        return peak_powers, peak_freqs, threshold, noise_lvl

    # ----------------------------------------------------------------------
    def bandwidth(self, f: np.ndarray, Pxx: np.ndarray, peak_freq: float, noise_lvl):
        """
        Calculate the bandwidth of a signal around a given peak frequency.

        This function identifies the bandwidth around a specified peak frequency by analyzing the power spectrum (Pxx).
        It determines where the slope of the spectrum changes from negative to positive to identify the edges of the bandwidth.

        Parameters
        ----------
        f : np.ndarray
            Array of frequency values in Hertz (Hz).
        Pxx : np.ndarray
            Power spectral density values corresponding to the frequencies in `f`.
        peak_freq : float
            The frequency at which the peak occurs, around which the bandwidth will be calculated.

        Returns
        -------
        BandwidthDetection
            A `BandwidthDetection` object containing the starting and ending frequencies of the bandwidth,
            as well as the dominant (peak) frequency.
        
        Raises
        ------
        ValueError
            If the calculated bandwidth is negative, which indicates an error in the input data or calculations.
        """
        peak_index = np.argmin(np.abs(f - peak_freq))
        for i in range(peak_index + 1, len(f)):
            if Pxx[i] < noise_lvl:
                bandwidth_right = f[i] - peak_freq
                break

        for i in range(peak_index - 1, -1, -1):
            if Pxx[i] < noise_lvl:
                bandwidth_left = peak_freq - f[i]
                break
            
        f_start = peak_freq - bandwidth_left
        f_end = peak_freq + bandwidth_right
        return f_start, f_end