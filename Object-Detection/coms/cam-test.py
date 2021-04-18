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

#Pyro4.naming.startNS(host='155.246.209.42', port=9090)



@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Master(object):
    def __init__(self):
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
        #while True:
        #    print('ree')
        detect.main()
        print("Done")

    def start_detection(self):
        self.create_process()
        self.p.start()

    def stop_detection(self):
        self.p.terminate()
        self.p.join()
        print('stop?')

def main():

    Pyro4.Daemon.serveSimple(
            {
                Master: "master-pi"
            },
            ns = True,
        )

if __name__=="__main__":
    main()