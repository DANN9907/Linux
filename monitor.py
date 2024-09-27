from hackrf import HackRF
import numpy as np
from typing import Union, Literal
from gcpds.filters import frequency as flt
import h5py
import os


########################################################################
class Scanning:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self,
                 vga_gain: int = 0,
                 lna_gain: int = 0,
                 sample_rate: float = 20e6,
                 overlap: int = 0,
                 time_to_read: float = 1,
                 ):
        """Initialize the Scanning object with the given parameters.

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
        self.hackrf = HackRF()
        self.hackrf.vga_gain = int(vga_gain)
        self.hackrf.lna_gain = int(lna_gain)
        self.hackrf.sample_rate = int(sample_rate)

        self.overlap = int(overlap)
        self.samples_to_read = int(self.hackrf.sample_rate * time_to_read)
        self.overlap_size = int(overlap * time_to_read)


    # ----------------------------------------------------------------------
    def scan(self, start: float, end: float) -> list[dict[str, Union[np.ndarray, float]]]:
        """Scan a frequency range and collect samples.

        Parameters
        ----------
        start : float
            Starting frequency in Hz.
        end : float
            Ending frequency in Hz.

        Returns
        -------
        list of dict
            A list of dictionaries where each dictionary contains:
            - 'start': float : Starting frequency of the scan window.
            - 'end': float : Ending frequency of the scan window.
            - 'samples': np.ndarray : Numpy array of samples.
            - 'sample_rate': float : Sample rate in Hz.
        """
        sample_rate = self.hackrf.sample_rate
        wide_samples = []
        
        steps = np.array(range(int(start+sample_rate/2), int((end+sample_rate/2)), int(sample_rate - self.overlap)))

        if start-end>self.hackrf.sample_rate:
            if steps[-2] + (sample_rate/2)>=end:
                steps = steps[:-1]

        for center_freq in steps:
            self.hackrf.center_freq = center_freq
            samples = np.array(self.hackrf.read_samples(self.samples_to_read))

            samples = samples - np.mean(samples)

            high100 = flt.GenericButterHighPass(f0=0.01, N=1)
            samples = high100(samples, fs=250)

            wide_samples.append({
                'start': center_freq,
                'end': center_freq + sample_rate,
                'samples': samples,
                'sample_rate': sample_rate,
                'overlap': self.overlap,
            })
        return wide_samples


    # ----------------------------------------------------------------------
    def concatenate(self, samples: list[dict[str, np.ndarray]], method: Literal['mean', 'half', 'drop_first', 'drop_second']) -> np.ndarray:
        """Concatenate samples from multiple scan windows, handling overlaps.

        This method concatenates the samples from multiple scan windows,
        handling overlapping regions according to the specified method.

        Parameters
        ----------
        samples : list of dict
            A list of dictionaries where each dictionary contains:
            - 'start': float : Starting frequency of the scan window.
            - 'end': float : Ending frequency of the scan window.
            - 'samples': np.ndarray : Array of samples.
            - 'sample_rate': float : Sample rate in Hz.
        method : Literal['mean', 'half', 'drop_first', 'drop_second']
            Method to handle overlapping regions:
            - 'mean': Average the overlapping regions.
            - 'half': Concatenate samples with half of the overlap size.
            - 'drop_first': Drop the first part of overlapping samples.
            - 'drop_second': Drop the second part of overlapping samples.

        Returns
        -------
        np.ndarray
            An array containing the concatenated samples with overlaps
            handled according to the specified method.
        """
        if not self.overlap:
            concatenated_samples = np.concatenate([sample_dict['samples'] for sample_dict in samples])
            return concatenated_samples
        else:

            match method:

                case 'mean':  # Calculate the mean overlap and concatenate the remaining samples
                    concatenated_samples = samples[0]['samples']
                    for sample in samples[1:]:
                        current_samples = sample['samples']
                        concatenated_samples[-self.overlap_size:] = (concatenated_samples[-self.overlap_size:] + current_samples[:self.overlap_size]) / 2
                        concatenated_samples = np.concatenate((concatenated_samples, current_samples[self.overlap_size:]))

                case 'half':  # Concatenate samples with half overlap
                    concatenated_samples = samples[0]['samples']
                    for sample in samples[1:]:
                        current_samples = sample['samples']
                        concatenated_samples = np.concatenate((concatenated_samples[:int(-self.overlap_size/2)], current_samples[int(self.overlap_size/2):]))

                case 'drop_first':  # Drop the first part of the overlapping samples and concatenate the remaining samples.
                    concatenated_samples = samples[0]['samples']
                    for sample in samples[1:]:
                        concatenated_samples = np.concatenate((concatenated_samples[:-self.overlap_size], sample['samples']))

                case 'drop_second':  # Drop the second part of the overlapping samples and concatenate the remaining samples.
                    concatenated_samples = samples[0]['samples']
                    for sample in samples[1:]:
                        concatenated_samples = np.concatenate((concatenated_samples, sample['samples'][self.overlap_size:]))

            return concatenated_samples



    # ----------------------------------------------------------------------
    def read(self):
        """"""


    # ----------------------------------------------------------------------
    def write(self, start: int=200e6, end: int=300e6, overlap: int=1000000, time_to_read: float=0.01, type_save: str='npy'):
        """
        Method to perform scanning and save the data.
        
        Parameters
        ----------
        start : float, optional
            Starting frequency in Hz (default is 88e6).
        end : float, optional
            Ending frequency in Hz (default is 128e6).
        time_to_read : float, optional
            Duration of time to read samples in seconds (default is 0.01).
        type_save : str, optional
            Format to save the samples (default is 'npy').
        """
        self.overlap = overlap
        self.samples_to_read = int(self.hackrf.sample_rate * time_to_read)
        self.overlap_size = int(self.overlap * time_to_read)

        wide_samples = self.scan(start, end)

        samples = self.concatenate(wide_samples, 'mean')

        if not os.path.exists('database'):
            os.makedirs('database')

        if type_save == 'npy':
            np.save(os.path.join('database', f'Samples {start/1e6} and {end/1e6}MHz with time to read {time_to_read}s and {overlap}MHz overlap.npy'), samples)
        elif type_save == 'h5':
            with h5py.File(os.path.join('database', f'Samples {start/1e6} and {end/1e6}MHz with time to read {time_to_read}s.npy and {overlap}MHz overlap.h5'), 'w') as hf:
                hf.create_dataset('samples', data=samples)