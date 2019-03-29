from rx import Observable
import struct
import threading
import traceback

from .client import Client


class Sensor(threading.Thread):

    def __init__(self, server_ip, config):
        threading.Thread.__init__(self)
        self.config = config
        self.id = config['type']+':'+config['id']
        self.client = Client(server_ip, config['listen_port'])
        self.source = Observable.create(self._init_rx).publish().auto_connect(1)

    def _init_rx(self, observer):
        self.observer = observer

    def start(self):
        self.should_stop = False
        self.client.connect()
        super().start()

    def stop(self):
        self.should_stop = True
        self.client.disconnect()
        self.join()

    def run(self):
        print("{0}: starting".format(self.id))
        while not self.should_stop:
            try:
                #print("reading header")
                header = self.client.read(12)
                #print("{0}: header = {1}".format(self.id, len(header)))

                length, time, gametime = struct.unpack("!IIf", header)
                #print("{0}: expecting {1} bytes".format(self.id, length))

                data = self.client.read(length - 12)
                #print("{0}: recv frame {1}".format(self.id, len(data)))
                self.observer.on_next((time, gametime, data))
            except Exception as e:
                print("{0}: exception {1}".format(self.id, str(e)))
                traceback.print_exc()
                break
        print("{0}: end".format((self.id)))