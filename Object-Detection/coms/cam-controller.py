'''
Don't forget to have this running!

python -m Pyro4.naming python -m Pyro4.naming -n 155.246.209.42

'''
import socket
import select
import sys

import subprocess
import Pyro4
import Pyro4.naming
from multiprocessing import Process, Lock
import detect

import board
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

#Pyro4.naming.startNS(host='155.246.209.42', port=9090)\


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Master(object):
    def __init__(self):
        self.kit = MotorKit(i2c=board.I2C())
        self.detected = False
        self.freq = 0.0
        self.transmit = False

    def show_transmit(self):
        return self.transmit
        
    def set_transmit_true(self):
        self.transmit = True

    def set_transmit_false(self):
        self.transmit = False

    def show_freq(self):
        return self.freq

    def drone_detected(self):
        return self.detected

    def swap_detected(self):
        self.detected = not self.detected

    def create_process(self):
        self.p = Process(target= self.run_detection)

    def run_detection(self):
        print("Starting Detection")
        detect.main()
       
    def start_detection(self):
        self.create_process()
        self.p.start()

    def stop_detection(self):
        try:
            self.kit.stepper1.release()
            self.p.terminate()
            self.p.join()
            print('Detection Stopped')
        except Exception as e:
            print(f'Either detection not running or {e}')

    def write_to_file(self, lines = ['No Drone Detected']):
        with open('Freq.txt' , 'w') as f:
            f.writelines(lines)
    




def main():
    #daemon = Pyro4.Daemon(host="192.168.1.24", port=9090)
    Pyro4.Daemon.serveSimple(
            {
                Master: "master-pi"
            },
            ns = True,
            host = '10.0.0.2',
            # port = 9091
        )

if __name__=="__main__":
    main()
