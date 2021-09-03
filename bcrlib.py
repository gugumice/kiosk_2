#!/usr/bin/env python3

import serial
import logging

class barCodeReader(object):
    def __init__(self, port='/dev/ttyACM0',
                 timeout=1):
        self.running=False
        self.bcr=None
        self.port=port
        self.timeout=timeout
        self.running=False
        self.next()

    def next(self):
        if self.bcr is None:
            try:
                self.bcr=serial.Serial(port=self.port,timeout=self.timeout)
            except Exception as e:
                self.running=False
                logging.error('{}'.format(e))
                return(None)
        try:
            self.running=True
            return(self.bcr.readline().decode('ascii').rstrip('\r\n'))

        except serial.serialutil.SerialException:
            logging.error('Lost communications with BC')
            self.running=False
            return(None)
def main():
    b=barCodeReader()
    while b.running:
        print(b.next())
if __name__ == "__main__":
    #logging.basicConfig(filename='/home/pi/kiosk.log',filemode='w',level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting")
