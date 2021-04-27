import sys
import Pyro4
import Pyro4.util


sys.excepthook = Pyro4.util.excepthook
master = Pyro4.Proxy("PYRONAME:master-pi@10.0.0.2:9090")

def main():
    print("Writing to File")
    master.write_to_file(['Test\n', 'T'])

if __name__ == '__main__':
    main()