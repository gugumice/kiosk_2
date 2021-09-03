#!/usr/bin/env python3
import logging
import cups

class printer():
    '''
    Class to set up and check printer status
    '''
    def __init__(self):
        self.error=None
        self._conn=None
        self.running=False
        self.defaultPrinter=None
        self._connected_printers=None
        self.set()
    def set(self):
        try:
            self._conn=cups.Connection()
        except self._conn.cups.IPPError as e:
            self.error=e
            return(False)
        self._connected_printers=self._conn.getDevices(include_schemes=['usb'])
        #Check if any usb: printere exist
        if len(self._connected_printers)==0:
            self.error='1: No usb: printers detected'
            return
        #If nstalled printer(s) not avilable
        self.defaultPrinter=self._conn.getDefault()
        if not self._installedIsAvilable():
            self.deletePrinters()
       
        #Add printer if default not present and usb: HP printer detected
        if self.defaultPrinter is None and self._connected_printers is not None:
            self.running = self.addPrinter()
            self.defaultPrinter=self._conn.getDefault()
        else:
            self.running = True
            self.deleteAllJobs()
        self.defaultPrinter=self._conn.getDefault()
    
    def deleteAllJobs(self):
        for p in self._connected_printers:
            try:
                self._conn.cancelAllJobs(p,my_jobs=True)
            except cups.IPPError:
                    pass 
    def _installedIsAvilable(self):
        #Check if CUPS printers are avilable. If not, delete & install any HP as default if avilable
        for ip in ([v['device-uri'] for k,v in self._conn.getPrinters().items()]):
            for ap in self._connected_printers:
                if ip==ap:
                    return(True)
        return(False)
        
    def addPrinter(self,driver='HP LaserJet Series PCL 6 CUPS'): 
        #Check if HP printer connected
        printer_make=driver.split(' ')[0]
        try:
            self.uri=[k for k,v in self._connected_printers.items() if v['device-make-and-model'].startswith(printer_make)][0]
            
        except:
            self.error='4: Add printer - no {} printer connected'.format(printer_make)
            return(False)
        
        #Get PPD for driver
        try:
            ppd_file = [k for k,v in self._conn.getPPDs().items()
             if v['ppd-make-and-model'] == driver][0]
        except:
            self.error = '4: Add printer - no PPD file for {}'.format(driver)
            return(False)
        printer_name=self._connected_printers[self.uri]['device-make-and-model']
        print_queue = printer_name.replace(' ','_')      
        try:
            self._conn.addPrinter(print_queue,ppdname=ppd_file,device=self.uri,info=printer_name)
            self._conn.setPrinterShared(print_queue,False)
            self._conn.setDefault(print_queue)
            self._conn.acceptJobs(print_queue)
            self._conn.enablePrinter(print_queue)
            self._conn.printTestPage(print_queue)
            logging.info('Printer {} added'.format(print_queue))
            return(True)
        except Exception as e:
            self.error = e
            return(False)

    def deletePrinters(self):
        installed_printers=self._conn.getPrinters()
        for p in installed_printers:
            logging.info('{} deleted'.format(p))
            self._conn.deletePrinter(p)

def main():
    c=printer()
    print('Error: {}, Status: {}'.format(c.error,c.running))
if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
