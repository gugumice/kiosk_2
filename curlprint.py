#!/usr/bin/env python3
import logging,os
from io import BytesIO
import cups,re
import pycurl
class curlGet():
    def __init__(self,url,timeout=10):
        self.PDFObj=BytesIO()
        self.error=None
        self.info=None
        self._c=pycurl.Curl()
        self._c.setopt(self._c.URL,url)
        self._c.setopt(self._c.CONNECTTIMEOUT,timeout)
        self._c.setopt(self._c.WRITEDATA,self.PDFObj)
        try:
            self._c.perform()
        except pycurl.error as e:
            self.error=[arg for arg in e.args]
        finally:
            self.info = self._c.getinfo(self._c.PRIMARY_IP)
            self._c.close()

def make_URL(bar_code,templ,host,lang):
    req_code = re.search(REG_EX,bar_code)
    if req_code is not None:
        req_code = req_code.group(0)
        req_code=req_code[1:].replace('#','%23')
        return(templ.format(host,req_code,lang))
    else:
        return(None)
def get_pdf(url,timeout=30):
    fileObj=BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.CONNECTTIMEOUT,timeout)
    c.setopt(c.WRITEDATA, fileObj)
    try:
        c.perform()
    except pycurl.error as e:
        logging.error(e)
        fileObj.write(str.encode(str(e)))
    finally:
        c.close
    return(fileObj)

def delete_all_jobs(conn):
    jobs_pending = conn.getJobs()
    for j in jobs_pending:
        logging.info('Deleting pending print job {}'.format(j))
        conn.cancelJob(j,purge_job=True)
    return(len(jobs_pending))

def print_report(fileObj,temp_file='/tmp/report.pdf'):
    conn=cups.Connection()
    prn=conn.getDefault()
    job_id=None
    #Create tmp file from BytesIO
    with open(temp_file, 'wb') as f:
        #f.write(fileObj.getvalue())
        f.write(fileObj.getbuffer())
    try:
        job_id=conn.printFile(prn,temp_file,'Report',{'print-color-mode': 'monochrome'})
        pass
    except cups.IPPError as e:
        logging.error('<print_report> {}'.format(e))
    finally:
        os.remove(temp_file)
    return(job_id)
def call_report(url):
    buffer=get_pdf(url,timeout=10)
    job_id=None
    if buffer.tell()>50:
        job_id=print_report(buffer)
        logging.info('Report sent to printer, jobID: {}'.format(job_id))
    else:
        logging.error(buffer.getvalue().decode('ascii'))
def main():
    url='http://10.100.50.104/csp/sarmite/ea.kiosk.pdf.cls?HASH=13621914%238444&LANG=RUS'
    URL='http://{}/csp/sarmite/ea.kiosk.pdf.cls?HASH={}&LANG={}'
    HOST='10.100.50.104'
    LANGUAGES=('LAT','ENG','RUS')
    url1=make_URL()
    call_report(url)
if __name__=='__main__':
   logging.basicConfig(format='%(asctime)s - %(message)s',level=logging.DEBUG)
   main()
