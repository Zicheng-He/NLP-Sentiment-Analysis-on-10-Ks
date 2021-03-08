
if __name__ == '__main__':
    from glob import glob
    import pysentiment2 as ps
    import Weight
    import DownloadandParse_10K
    import P3
    import numpy as np
    import pandas as pd
    set_hv = ps.HIV4()._negset
    df = pd.read_csv(r'/Users/ruochengzhang/Desktop/FRE 7871 NLP/Project 1/nega.csv')
    set_lm = set(df['Words'].str.lower())
    """"""""""
    Download
    ******************************************
    f_10K = ['10-K', '10-K405', '10KSB', '10-KSB', '10KSB40']
    # -----------------------
    # User defined parameters
    # -----------------------
    
    # List target forms as strings separated by commas (case sensitive) or
    #   load from EDGAR_Forms.  (See EDGAR_Forms module for predefined lists.)
    PARM_FORMS = f_10K  # or, for example, PARM_FORMS = ['8-K', '8-K/A']
    PARM_BGNYEAR = 2010  # User selected bgn period.  Earliest available is 1994
    PARM_ENDYEAR = 2019  # User selected end period.
    PARM_BGNQTR = 1  # Beginning quarter of each year
    PARM_ENDQTR = 4  # Ending quarter of each year
    # Path where you will store the downloaded files
    PARM_PATH = r'/Users/ruochengzhang/Desktop/FRE 7871 NLP/Project 1/Files/'
    # Change the file pointer below to reflect your location for the log file
    #    (directory must already exist)
    PARM_LOGFILE = (r'/Users/ruochengzhang/Desktop/FRE 7871 NLP/Project 1/Log/' +
                    str(PARM_BGNYEAR) + '-' + str(PARM_ENDYEAR) + '.txt')
    OutPutPath = r"/Users/ruochengzhang/Desktop/FRE 7871 NLP/Project 1/Output/"
    # EDGAR parameter
    PARM_EDGARPREFIX = 'https://www.sec.gov/Archives/'
    # Dow30 CIK list
    Dow30 = pd.read_excel("/Users/ruochengzhang/Desktop/FRE 7871 NLP/Project 1/dow30_complete.xlsx")
    CIK_Ticker = {cik:symbol for cik,symbol in zip(Dow30['CIK'],Dow30['co_tic'])}
    CIK_list = list(Dow30['CIK'])
    start = time.perf_counter()
    print('\n' + time.strftime('%c') + '\nND_SRAF:  Program EDGAR_DownloadForms.py\n')
    download_forms()
    print('\nEDGAR_DownloadForms.py | Normal termination | ' +
          time.strftime('%H:%M:%S', time.gmtime(time.perf_counter() - start)))
    print(time.strftime('%c'))

    ### Transform
    ********************************************
    # DownloadandParse_10K.reform_parse(PARM_PATH, OutPutPath) or
    PARM_PATH = r'/Users/ruochengzhang/Desktop/FRE 7871 NLP/Project 1/Files/'
    OutPutPath = r"/Users/ruochengzhang/Desktop/FRE 7871 NLP/Project 1/Output2/"
    DownloadandParse_10K.reform_parse2(PARM_PATH, OutPutPath)
    """""""""""

    dict_path = r'/Users/ruochengzhang/Desktop/FRE 7871 NLP/Project 1/Output/'
    txt_file_list = glob(dict_path+'*.txt')
    documents = [open(i, "r").read() for i in txt_file_list]
    split_lis = [i.split("_") for i in txt_file_list]
    date_lis = [i[0][-8:] for i in split_lis]
    tic_lis = [i[1][:-4] for i in split_lis]
    term_hv, term_lm, prop_hv, prop_lm, c_hv, c_lm = Weight.problem2(documents, set_hv, set_lm)
    number_of_10k = len(documents)
    'CRSP is used for benchmark'
    df_crsp = pd.read_csv(r'/Users/ruochengzhang/Desktop/FRE 7871 NLP/Project 1/crsp.csv',index_col='date')
    final_matrix = P3.calculation(number_of_10k,tic_lis,date_lis,df_crsp,term_hv,term_lm,prop_hv,prop_lm,c_hv, c_lm)
    P3.plott(final_matrix, number_of_10k)


