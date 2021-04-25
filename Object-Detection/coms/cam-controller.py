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

    def show_freq(self):
        return self.freq

    def drone_detected(self):
        return self.detected

    def swap_detected(self):
        self.detected = not self.detected

    def create_process(self):
        self.p = Process(target= self.run_detection)

    def run_detection(self):
        detect.main()
        print("Detection Running")

    def start_detection(self):
        self.create_process()
        self.p.start()

    def stop_detection(self):
        self.kit.stepper1.release()
        self.p.terminate()
        self.p.join()
        print('Detection Stopped')

def main():
    #daemon = Pyro4.Daemon(host="192.168.1.24", port=9090)
    Pyro4.Daemon.serveSimple(
            {
                Master: "master-pi"
            },
            ns = True,
            host = '10.0.0.2',
            port = 9091
        )

if __name__=="__main__":
    main()
