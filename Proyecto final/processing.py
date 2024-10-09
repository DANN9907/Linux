import numpy as np
import pandas as pd
from scipy.signal import welch

class Processing:

    # ----------------------------------------------------------------------
    def welch(self, signal: np.ndarray, fs: float = 20e6) -> np.ndarray:
        """
        Estimate the power spectral density of the given signal using Welch's method.

        Parameters
        ----------
        signal : np.ndarray
            An array representing the signal to be analyzed where
            the real part is the in-phase component (I) and the imaginary part
            is the quadrature component (Q).
        fs : float, optional
            The sampling frequency of the signal. Default is 20M.

        Returns
        -------
        numpy.ndarray
            The estimated power spectral density of the signal.

        Raises
        ------
        ValueError
            If the input signal is not a numpy array.

        Notes
        -----
        This method utilizes Welch's algorithm, implemented in NumPy, to estimate
        the power spectral density of the signal. The signal is divided into
        overlapping segments, windowed, and then averaged to reduce variance.
        """

        """
        nperseg: int, optional
            Specifies the number of points in each segment. During the calculation of the 
            PSD using the Welch method, the signal is divided into segments, 
            and the PSD is calculated for each segment

            Length of each segment. Defaults to None, but if window is str or tuple, 
            is set to 256, and if window is array_like, is set to the length of the window.

        noverlap: int, optional
            Specifies the number of overlap points between consecutive segments. 
            By overlaying the segments, a smoother and less noisy estimate of the PSD is obtained

            Number of points to overlap between segments. If None, noverlap = nperseg // 2. Defaults to None.
        """

        if not isinstance(signal, np.ndarray):
            raise ValueError("Input signal must be un numpy array")

        f, Pxx = welch(signal, fs=fs, nperseg=4096, window=('kaiser', 20), scaling='density')

        f = np.fft.fftshift(f)
        Pxx = np.fft.fftshift(Pxx)
        return f, Pxx