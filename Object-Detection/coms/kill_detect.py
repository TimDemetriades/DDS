import Pyro4

master = Pyro4.Proxy("PYRONAME:master-pi@10.0.0.2:9090")

def main():
    print("Stopping Detection")
    master.stop_detection()

if __name__ == '__main__':
    main()