import time
import sys
import os
import Pyro4
import Pyro4.util
from multiprocessing import Process, Lock
import threading


sys.excepthook = Pyro4.util.excepthook
master = Pyro4.Proxy("PYRONAME:master-pi@192.168.1.24:9090")

def main():
    print(master.drone_detected())
    master.swap_detected()
    print(master.drone_detected())
    
    
    master.start_detection()
    print('Detection Started')
    time.sleep(1000)
    master.stop_detection()
    print('Dectection Stopped')
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        master.stop_detection()
        print('Dectection Stopped')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)



# print(f'run = {master.show_run()}')
# p1 = Process(target= master.start_detection)
# print(f'reee')
# p1.start()
# print(f'reee1')
# p2 = Process(target= master.stop_detection, daemon=True)
# print(f'reee2')
# p2.start()
# print(f'reee3')
# p2.join()
# print(f'reee4')
# p1.join()
# print(f'run = {master.show_run()}')
# print('here')
