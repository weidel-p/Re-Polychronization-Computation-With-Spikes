import numpy as np
import matplotlib.pyplot as plt

colors=['b','g','r','purple','black','y','cyan','r','r','r','r','r','r','r']
def match_pattern(times,senders,t,group,threshold=0.4):
    count=1
    adjusted_time = times - t
    for i,neuron in enumerate(group['senders']):
        t_window=adjusted_time-group['times'][i]
        p0=abs(t_window)<=2.
        target=senders[p0]
        if neuron in target:
            count+=1
    if group['N']*threshold<=count*1.0:
        return True,count*1.0/group['N']
    else:
        return False,count*1.0/group['N']

def bin_pop_rate(times, senders, binwidth=1.):
	t_min = np.min(times)
	t_max = np.max(times)
	N_senders = len(np.unique(senders))
	rate, bin_edges = np.histogram(times, np.arange(t_min, t_max, binwidth))
	return rate * 1000 / (N_senders * binwidth), bin_edges[:-1]

def calc_specgram(time,rate,NFFT=1024,noverlap=900):
	Pxx, freqs, bins, im = plt.specgram(rate, NFFT=NFFT, Fs=1000./(time[2]-time[1]), noverlap=noverlap)
	return freqs,Pxx,bins

