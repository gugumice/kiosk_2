#!/usr/bin/env python3
import argparse
import re, threading
from time import sleep,time
import logging
from ledslib import ledButtons, pushButtons
from bcrlib import barCodeReader
from printerlib import printer
import threading
from curlprint import *

BUTTON_PINS=(17,27,22)
LED_PINS=(13,19,26)
BUZ_PIN=12
HOST='10.100.50.104'
REG_EX='^\d{7,9}#\d{4,5}'
PORT='/dev/ttyACM0'
DEFAULT_BUTTON=0
LANGUAGES=('LAT','ENG','RUS')
BUTTON_TIMEOUT=10 #Button timeout in secs
BCR_TIMEOUT=1 #Barcode reader timeout in secs
CURL_TIMEOUT=15 #Curl connection timeout
REPORT_DELAY=10 #Seconds to wait for report printout
BUTTON_PRINTER_RESET=1 #Button to activate printer reset at startup
URL='http://{}/csp/sarmite/ea.kiosk.pdf.cls?HASH={}&LANG={}'
#Watchdog device name - Node: WD disabled 
#WD=None
WD='/dev/watchdog'
#WD object
wdObj=None

def start_watchog(watchdog_device):
    try:
        dev=open(watchdog_device,'w')
    except:
        dev = None
    return(dev)
wdObj=start_watchog(WD)

def update_leds(l,b):
    logging.info('Active button: {}'.format(b))
    l.off()
    l.on(b,s=True)
    return(b)

def make_URL(bar_code,templ,host,lang):
    if bar_code[0]=='#':
        bar_code=bar_code[1:]
    req_code = re.search(REG_EX,bar_code)
    if req_code is not None:
        req_code = req_code.group(0)
        req_code=req_code.replace('#','%23')
        return(templ.format(host,req_code,lang))
    else:
        return(None)

def check_list(leds,bcr,bttn,host):
    for l in range(0,leds.num_leds()):
        leds.on(l,s=True)
        sleep(1)
    #Check if barcode reader is OK
    while not bcr.running:
        leds.blink(led=2)
        bcr.next()
    sleep(.5)
    leds.off(2)
    #Check if printer OK
    prn=printer()
    if bttn.pressed() == BUTTON_PRINTER_RESET:
        logging.info('User printer reset init')
        prn.deleteAllJobs()
        prn.deletePrinters()
        prn.set()
    while not prn.running:
        leds.blink(led=1)
        prn.set()
    sleep(.5)
    leds.off(1)
    #Check connection with server
    curl=curlGet('http://{}/'.format(host),timeout=CURL_TIMEOUT)
    while not curl.info==host:
        leds.blink(led=0)
        curl=curlGet('http://{}/'.format(host))
    sleep(.5)
    leds.off(0)
    sleep(.5)
    prn=None
    curl=None

def main(args):
    if args.port is None:
        port=PORT
    if args.host is None:
        host=HOST
    logging.info('Watchdog {}'.format('disabled' if wdObj is None else 'enabled'))
    active_button=DEFAULT_BUTTON
    leds=ledButtons(LED_PINS,BUZ_PIN)
    bttn=pushButtons(BUTTON_PINS,timeout=BUTTON_TIMEOUT)
    bcr=barCodeReader(port,BCR_TIMEOUT)
    check_list(leds,bcr,bttn,host)
    #Check list OK
    leds.blink(s=True)
    #Set default button/lang on
    leds.on(active_button)
    #Main loop
    while bcr.running:
        #Pat watchdog if on
        if WD is not None:
            print('1',file = wdObj, flush = True)
        #Monitor buttons
        if bttn.pressed() is not None:
            active_button=update_leds(leds,bttn.pressed())
        if bttn.timed_out():
            if active_button != DEFAULT_BUTTON:
                active_button=update_leds(leds,DEFAULT_BUTTON)
        buffer=bcr.next()
        if len(buffer)>0:
            #logging.info('<{}>'.format(buffer))
            url=make_URL(buffer,URL,HOST,LANGUAGES[active_button])
            logging.info('URL {}'.format(url))
            if url is not None:
                job_start=time()
                t = threading.Thread(target=call_report, args=(url,))
                t.start()
                bttn.reset()
                logging.info('Report thread started')
                #wawe LEDs if thread active or REPORT_DELAY not reached
                while t.is_alive() or (time()<job_start+REPORT_DELAY):
                    leds.wave()
            leds.off()
            sleep(1)
            leds.on(active_button)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print report')
    parser.add_argument('-port', metavar='port', type=str, help='Port for barcode reader')
    parser.add_argument('-host', metavar='host', type=str, help='5M host')
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s - %(message)s',filename='/home/pi/kiosk.log',filemode='w',level=logging.DEBUG)
    #logging.basicConfig(format='%(asctime)s - %(message)s',level=logging.DEBUG)
    try:
        main(args)
    except KeyboardInterrupt:
        if wdObj is not None:
            print('V',file = wdObj, flush = True)
        print("\nExiting")
