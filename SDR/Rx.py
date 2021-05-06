import numpy as np
import adi

import time
import sys
import os
import Pyro4
import Pyro4.util
from multiprocessing import Process, Lock
import threading

from gnuradio import analog
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import iio


sys.excepthook = Pyro4.util.excepthook
master = Pyro4.Proxy("PYRONAME:master-pi@10.0.0.2:9090")

lo = True

rxlo1 = 2.4305e9
rxlo2 = 2.4455e9

sdr = adi.Pluto()
sdr.rx_lo = int(rxlo1)
sdr.rx_rf_bandwidth = int(56e6)
sdr.sample_rate = int(40e6)
sdr.rx_buffer_size = 1024

print(sdr)

class tx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 40e6
        self.fc = fc = int(2.4e9)

        ##################################################
        # Blocks
        ##################################################
        self.iio_pluto_sink_0 = iio.pluto_sink('ip:pluto.local', fc, int(samp_rate), 15000000, 32768, True, 0.0, '', True)
        self.channels_channel_model_1 = channels.channel_model(
            noise_voltage=40,
            frequency_offset=0.0,
            epsilon=1.0,
            taps=[1.0 + 1.0j],
            noise_seed=0,
            block_tags=False)
        self.analog_sig_source_x_1 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 1000, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_1, 0), (self.channels_channel_model_1, 0))
        self.connect((self.channels_channel_model_1, 0), (self.iio_pluto_sink_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)
        self.iio_pluto_sink_0.set_params(self.fc, int(self.samp_rate), 15000000, 0.0, '', True)

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.iio_pluto_sink_0.set_params(self.fc, int(self.samp_rate), 15000000, 0.0, '', True)


def Jam(fc, top_block_cls=tx, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sdr.tx_harwaregain_chan0 = -80
        sdr.tx_destroy_buffer()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    sdr.tx_lo = int(fc)

    while master.show_transmit:
        print("TRANSMITTING!")

    tb.stop()
    tb.wait()
    sdr.tx_hardwaregain_chan0 = -80
    sdr.tx_destroy_buffer()

    # try:
    #     input('Press Enter to quit: ')
    # except EOFError:
    #     pass
    # tb.stop()
    # tb.wait()

def FFT(samples, buf, samprate, lo):
    fft = np.fft.fftshift(np.fft.fft(samples)) / buf
    freqLabels = np.fft.fftshift(np.fft.fftfreq(buf, 1/samprate)) + lo
    fft_mag_dB = 10*np.log10(np.abs(fft))
#     fft_mag = np.abs(fft)
    return fft_mag_dB, freqLabels

def MA(data):
    N = 10
    w = np.ones(N) / N
    ma = np.convolve(data, w, mode='same')
    return(ma)

def findSigPts(boolarray):
    a = boolarray^np.concatenate(([False],boolarray[:-1]))
    return(abs(a))

def findBWs(sigpts):
    freqs = np.zeros([len(sigpts)-1,2])
    freqs[:,0] = sigpts[1:]
    freqs[:,1] = sigpts[:-1]
    BWs = (sigpts[1:]-sigpts[:-1])/1e6
    return BWs, freqs

def findSigSec(boolarray):
    SigSections = []
    for i in range(1,len(boolarray)):
        if boolarray[i-1]:
            if i == 1:
                SigSections.append(1)
            if not boolarray[i]:
                SigSections.append(0)
        elif not boolarray[i-1]:
            if boolarray[i]:
                SigSections.append(1)

    return np.array(SigSections[:-1]).astype(np.bool)

switch_flag = False
stop = True
start = True
nothere = 0
stop_thresh = 0
while (True):
    ct = 0
    guess = 0
    for i in range(100):
        samples = sdr.rx()
        droneFreqData, droneFreqLabels = FFT(sdr.rx(), sdr.rx_buffer_size, sdr.sample_rate, sdr.rx_lo)

        freq_ndb = 10**(droneFreqData/10)
        freq_ma = MA(droneFreqData)
        freq_ma_ndb = MA(freq_ndb)
        ma_thresh = freq_ndb.mean()*1.5

        if (np.sum(freq_ma_ndb > ma_thresh) > 0):
            BWs, freqRgs= findBWs(droneFreqLabels[findSigPts(freq_ma_ndb > ma_thresh)])
            sigSec = findSigSec(freq_ma_ndb > ma_thresh)
            sigBWs = BWs[sigSec][(BWs[sigSec] > 9) & (BWs[sigSec] < 12)]
            drone_sig_range = freqRgs[sigSec][(BWs[sigSec] > 9) & (BWs[sigSec] < 12)]

        if sigBWs.size >= 1:
            ct += 1
            guess += (drone_sig_range[0,0]-drone_sig_range[0,1])/2 + drone_sig_range[0,1]

    if switch_flag:
        if lo:
            print(f"NOW AT LO: {rxlo2}")
            sdr.rx_lo = int(rxlo2)
            lo = False
        else:
            print(f"NOW AT LO: {rxlo1}")
            sdr.rx_lo = int(rxlo1)
            lo = True
        switch_flag = False

    if ct > 5:
        # with open("./drone_loc.txt", 'w') as f:
        #     f.write(str(guess/ct))
        # f.close()
        master.write_to_file(lines= f"{np.float32(guess/ct / 1e9):.4f} GHz")
        if start:
            print("starting obj detection...")
            master.start_detection()
            start = False
            stop = True
            stop_thresh = 0
        nothere = 0
        print(f"drone located at {guess/ct}")
        print(f"tx?:  {master.show_transmit()}")
        # jam
        #Jam(guess/ct)

    else:
        nothere += 1

    if nothere > 5:
        stop_thresh += 1
        switch_flag = True
        nothere = 0
        if stop_thresh > 2 and stop:
            print("STOPING OBJ DETECTION...")
            master.stop_detection()
            stop = False
            start = True
        print("SWITCHING LO")

    print(f"Number of Guesses: {ct}")
