
import numpy as np
import adi
from scipy import signal





sdr = adi.Pluto()
sdr.tx_hardwaregain_chan0 = -80 # Increase to increase tx power, valid range is -90 to 0 dB
sdr.tx_destroy_buffer()
