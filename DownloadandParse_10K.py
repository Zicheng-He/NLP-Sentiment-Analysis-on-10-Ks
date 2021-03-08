# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 16:17:16 2020

@author: Hans He
"""
import os
import time
from urllib.request import urlretrieve
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
import pandas as pd

import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
response = urllib.request.urlopen('https://www.python.org')




#
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * +


# Download Master.idx from EDGAR, this file contain every txt file in SEC, categorized by year and quarter
def download_masterindex(year, qtr, flag=False):
    # Download Master.idx from EDGAR
    # Loop accounts for temporary server/ISP issues
    # ND-SRAF / McDonald : 201606

    number_of_tries = 10
    sleep_time = 10  # Note sleep time accumulates according to err

    PARM_ROOT_PATH = 'https://www.sec.gov/Archives/edgar/full-index/'

    start = time.perf_counter()  # Note: using clock time not CPU
    masterindex = []
    #  using the zip file is a little more complicated but orders of magnitude faster
    append_path = str(year) + '/QTR' + str(qtr) + '/master.zip'  # /master.idx => nonzip version
    sec_url = PARM_ROOT_PATH + append_path

    for i in range(1, number_of_tries + 1):
        try:
            zipfile = ZipFile(BytesIO(urlopen(sec_url).read()))
            records = zipfile.open('master.idx').read().decode('utf-8', 'ignore').splitlines()[10:]
#           records = urlopen(sec_url).read().decode('utf-8').splitlines()[10:] #  => nonzip version
            break
        except Exception as exc:
            if i == 1:
                print('\nError in download_masterindex')
            print('  {0}. _url:  {1}'.format(i, sec_url))

            print('  Warning: {0}  [{1}]'.format(str(exc), time.strftime('%c')))
            if '404' in str(exc):
                break
            if i == number_of_tries:
                return False
            print('     Retry in {0} seconds'.format(sleep_time))
            time.sleep(sleep_time)
            sleep_time += sleep_time


    # Load m.i. records into masterindex list
    for line in records:
        mir = MasterIndexRecord(line)
        if not mir.err:
            masterindex.append(mir)

    if flag:
        print('download_masterindex:  ' + str(year) + ':' + str(qtr) + ' | ' +
              'len() = {:,}'.format(len(masterindex)) + ' | Time = {0:.4f}'.format(time.perf_counter() - start) +
              ' seconds')

    return masterindex

### Setting a class so that each record in master index can be store in the members with corresponding info
class MasterIndexRecord:
    def __init__(self, line):
        self.err = False
        parts = line.split('|')
        if len(parts) == 5:
            self.cik = int(parts[0])
            self.name = parts[1]
            self.form = parts[2]
            self.filingdate = int(parts[3].replace('-', ''))
            self.path = parts[4]
            self.ticker = ''
            if self.cik in CIK_list:
                self.ticker = CIK_Ticker[self.cik]
        else:
            self.err = True
        return

### when not available for bulk download, try 10 min later, but here we set up the timer so that can get access to it anytime
def edgar_server_not_available(flag=False):
    # routine to run download only when EDGAR server allows bulk download.
    # see:  https://www.sec.gov/edgar/searchedgar/ftpusers.htm
    # local time is converted to EST for check

    from datetime import datetime as dt
    import pytz
    import time

    SERVER_BGN = 0  # Server opens at 9:00PM EST
    SERVER_END = 24   # Server closes at 6:00AM EST

    # Get UTC time from local and convert to EST
    utc_dt = pytz.utc.localize(dt.utcnow())
    est_timezone = pytz.timezone('US/Eastern')
    est_dt = est_timezone.normalize(utc_dt.astimezone(est_timezone))

    if est_dt.hour >= SERVER_BGN or est_dt.hour < SERVER_END:
        return False
    else:
        if flag:
            print('\rSleeping: ' + str(dt.now()), end='', flush=True)
        time.sleep(600)  # Sleep for 10 minutes
        return True

### store the txt file into local path
def download_to_file(_url, _fname, _f_log=None):
    # download file from 'url' and write to '_fname'
    # Loop accounts for temporary server/ISP issues

    number_of_tries = 10
    sleep_time = 10  # Note sleep time accumulates according to err

    for i in range(1, number_of_tries + 1):
        try:
            urlretrieve(_url, _fname)
            return
        except Exception as exc:
            if i == 1:
                print('\n==>urlretrieve error in download_to_file.py')
            print('  {0}. _url:  {1}'.format(i, _url))
            print('     _fname:  {0}'.format(_fname))
            print('     Warning: {0}  [{1}]'.format(str(exc), time.strftime('%c')))
            if '404' in str(exc):
                break
            print('     Retry in {0} seconds'.format(sleep_time))
            time.sleep(sleep_time)
            sleep_time += sleep_time

    print('\n  ERROR:  Download failed for')
    print('          url:  {0}'.format(_url))
    print('          _fname:  {0}'.format(_fname))
    if _f_log:
        _f_log.write('ERROR:  Download failed=>')
        _f_log.write('  _url: {0:75}'.format(_url))
        _f_log.write('  |  _fname: {0}'.format(_fname))
        _f_log.write('  |  {0}\n'.format(time.strftime('%c')))

    return

### main function for the download part
def download_forms():
    # Download each year/quarter master.idx and save record for requested forms
    f_log = open(PARM_LOGFILE, 'a')
    f_log.write('BEGIN LOOPS:  {0}\n'.format(time.strftime('%c')))
    n_tot = 0
    n_errs = 0
    for year in range(PARM_BGNYEAR, PARM_ENDYEAR + 1):
        for qtr in range(PARM_BGNQTR, PARM_ENDQTR + 1):
            startloop = time.perf_counter()
            n_qtr = 0
            file_count = {}
            # Setup output path
            path = '{0}{1}\\QTR{2}\\'.format(PARM_PATH, str(year), str(qtr))
            if not os.path.exists(path):
                os.makedirs(path)
                print('Path: {0} created'.format(path))
            masterindex = download_masterindex(year, qtr, True)
            if masterindex:
                for item in masterindex:
                    while edgar_server_not_available(True):  # kill time when server not available
                        pass
                    if (item.form in PARM_FORMS) & (item.cik in CIK_list):
                        n_qtr += 1
                        # Keep track of filings and identify duplicates
                        fid = str(item.cik) + str(item.filingdate) + item.form
                        if fid in file_count:
                            file_count[fid] += 1
                        else:
                            file_count[fid] = 1
                        # Setup EDGAR URL and output file name
                        url = PARM_EDGARPREFIX + item.path
                        fname = (path + str(item.filingdate) + '_' + item.ticker + '_' + item.form.replace('/', '-') + '_' +
                                 item.path.replace('/', '_'))
                        fname = fname.replace('.txt', '_' + str(file_count[fid]) + '.txt')
                        return_url = download_to_file(url, fname, f_log)
                        if return_url:
                            n_errs += 1
                        n_tot += 1
                        # time.sleep(1)  # Space out requests
            print(str(year) + ':' + str(qtr) + ' -> {0:,}'.format(n_qtr) + ' downloads completed.  Time = ' +
                  time.strftime('%H:%M:%S', time.gmtime(time.perf_counter() - startloop)) +
                  ' | ' + time.strftime('%c'))
            f_log.write('{0} | {1} | n_qtr = {2:>8,} | n_tot = {3:>8,} | n_err = {4:>6,} | {5}\n'.
                        format(year, qtr, n_qtr, n_tot, n_errs, time.strftime('%c')))

            f_log.flush()

    print('{0:,} total forms downloaded.'.format(n_tot))
    f_log.write('\n{0:,} total forms downloaded.'.format(n_tot))



### When we get the text files, they contain the html format, here we use BeautiSoup to parse them into readable text files.
### Re-form Parsing
from glob import glob
from bs4 import BeautifulSoup
import re

### There are two ways to parse the original downloaded text files(with html format) into human-readable text
def reform_parse2(dict_path, output_path):
    txt_file_list = glob(dict_path + '*\*\*.txt')
    for filename in txt_file_list:
        filenamesplit = filename.split('\\')[-1].split('_')
        filedate = filenamesplit[0]
        fileticker = filenamesplit[1]

        file1 = open(filename, "r+", encoding='utf-8')
        data = file1.read()

        soup = BeautifulSoup(data, 'lxml')
        transformed_data = soup.get_text()
        file2 = open(output_path + filedate + '_' + fileticker + '.txt', "w+", encoding='utf-8')
        print(transformed_data, file=file2)
        file1.close()
        file2.close()
        print('Parsed file: ' + filename)

### Second way to do it, basically just select the document part in the file, so that the output is much cleaner.
def reform_parse(dict_path, output_path):
    txt_file_list = glob(dict_path+'*\*\*.txt')
    for filename in txt_file_list:
        filenamesplit = filename.split('\\')[-1].split('_')
        filedate = filenamesplit[0]
        fileticker = filenamesplit[1]
        
        file1 = open(filename,"r+",encoding='utf-8')
        data = file1.read()
        
        # Regex to find <DOCUMENT> tags
        doc_start_pattern = re.compile(r'<DOCUMENT>')
        doc_end_pattern = re.compile(r'</DOCUMENT>')
        # Regex to find <TYPE> tag prceeding any characters, terminating at new line
        type_pattern = re.compile(r'<TYPE>[^\n]+')
        
        # Create 3 lists with the span idices for each regex
        
        ### There are many <Document> Tags in this text file, each as specific exhibit like 10-K, EX-10.17 etc
        ### First filter will give us document tag start <end> and document tag end's <start> 
        ### We will use this to later grab content in between these tags
        doc_start_is = [x.end() for x in doc_start_pattern.finditer(data)]
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(data)]
        
        ### Type filter is interesting, it looks for <TYPE> with Not flag as new line, ie terminare there, with + sign
        ### to look for any char afterwards until new line \n. This will give us <TYPE> followed Section Name like '10-K'
        ### Once we have have this, it returns String Array, below line will with find content after <TYPE> ie, '10-K' 
        ### as section names
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(data)]
        document = {}    
        # Create a loop to go through each section type and save only the 10-K section in the dictionary
        for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
            if doc_type == '10-K':
                document[doc_type] = data[doc_start:doc_end]
        data10k = document['10-K']    
        soup = BeautifulSoup(data10k, 'lxml') ### Another Optional parser: html
        transformed_data = soup.get_text()
        file2 = open(output_path+filedate+'_'+fileticker+'.txt',"w+",encoding='utf-8')
        print(transformed_data, file=file2)
        file1.close()
        file2.close()
        print('Parsed file: '+ filename)




