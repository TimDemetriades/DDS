
import numpy as np
import adi
from scipy import signal



sample_rate = 10e6 # Hz
center_freq = 2.4385e9 # Hz


sdr = adi.Pluto()
sdr.tx_rf_bandwidth = int(sample_rate) # filter cutoff, just set it to the same as sample rate
sdr.tx_lo = int(center_freq)
sdr.tx_hardwaregain_chan0 = 0 # Increase to increase tx power, valid range is -90 to 0 dB

samples = np.random.normal(0,1,10000) + 1j*np.random.normal(0,1,10000)
samples /= max(samples)
samples *= 2**14

sdr.tx_cyclic_buffer=1 # Enable cyclic buffers
sdr.tx(samples)
