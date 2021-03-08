import yfinance as yf
import datetime
import Weight
import pandas as pd
import numpy as np



"date format like '20140425'"
# The function returns the excess return defined in the paper for each 10-K
def excess_return(ticker, date, df_crsp):
    tic = yf.Ticker(ticker)
    try:
        d1 = df_crsp.index.get_loc(int(date))
    except KeyError:
        d1 = df_crsp.index.get_loc(int(date)-1)
    d2 = d1+3
    date1 = datetime.datetime.strptime(str(df_crsp.index[d1]),'%Y%m%d')
    date1 = datetime.datetime.strftime(date1,'%Y-%m-%d')
    date2 = df_crsp.index[d2]
    date2 = datetime.datetime.strptime(str(date2),'%Y%m%d')
    date2 = datetime.datetime.strftime(date2,'%Y-%m-%d')
    date3 = df_crsp.index[d2+1]
    date3 = datetime.datetime.strptime(str(date3),'%Y%m%d')
    date3 = datetime.datetime.strftime(date3,'%Y-%m-%d')
    try:
        p = tic.history(start=date1,end=date3)['Close']
        cr = df_crsp.loc[df_crsp.index[d2],]/df_crsp.loc[int(date),] -1
        excess_r = p.loc[date2,]/p[0] - 1 - cr
    except IndexError:
        print(date1,date2,p)
    return excess_r


# This function returns a matrix of size (N,5)
# The first dimension is jth 10K, the next dimension is for its term weight etc.
def calculation(N,ticker_lis,date_lis,df_crsp,term_hv,term_lm,prop_hv,prop_lm,c_hv,c_lm):
    "for each 10K we will store its term weight for havard dic & LM dic, proportional weight"
    "for havard dic & LM dic and its excess return"
    final_matrix = np.zeros((N,5))
    for i in range(0,N):
        ticker = ticker_lis[i]
        date = date_lis[i]
        final_matrix[i][0] = np.dot(c_hv[:, i],term_hv[:, i])
        final_matrix[i][1] = np.dot(c_lm[:, i],term_lm[:, i])
        final_matrix[i][2] = np.sum(prop_hv[:, i])
        final_matrix[i][3] = np.sum(prop_lm[:, i])
        final_matrix[i][4] = excess_return(ticker, date, df_crsp)
    return final_matrix

# This function draw the required plot based on percentile
def plott(final_matrix,N):
    "N is the total number of 10-Ks"
    import matplotlib.pyplot as plt
    import matplotlib.ticker as plticker
    temp = int(N / 5)
    har_term = final_matrix[np.argsort(final_matrix[:, 0])][:,-1]
    lm_term = final_matrix[np.argsort(final_matrix[:, 1])][:,-1]
    har_prop = final_matrix[np.argsort(final_matrix[:, 2])][:,-1]
    lm_prop = final_matrix[np.argsort(final_matrix[:, 3])][:,-1]
    h_t,l_t,h_p,l_p = [],[],[],[]
    for i in range(0,5):
        h_t.append(np.median(har_term[i * temp:(i + 1) * temp]))
        l_t.append(np.median(lm_term[i * temp:(i + 1) * temp]))
        h_p.append(np.median(har_prop[i * temp:(i + 1) * temp]))
        l_p.append(np.median(lm_prop[i * temp:(i + 1) * temp]))


    fig, axs = plt.subplots(1, 2, sharex=True)
    x = ['Low',2,3,4,'High']
    axs[0].plot(x, h_t, "-o", color="r", label='har_term')
    axs[0].plot(x, l_t, "-o", color="black", label='lm_term')
    axs[0].legend()
    axs[0].set_title("Excess Return for Term Weight")
    axs[0].set_xlabel("Quantile")
    axs[1].plot(x, h_p, "-o", color="r", label='har_prop')
    axs[1].plot(x, l_p, "-o", color="black", label='lm_prop')
    axs[1].legend()
    axs[1].set_title("Excess Return for Proportional Weight")
    axs[1].set_xlabel("Quantile")


    plt.show()