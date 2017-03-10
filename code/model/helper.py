import numpy as np
import nest
import matplotlib.pyplot as plt
from params import *

colors=['b','g','r','purple','black','y','cyan','r','r','r','r','r','r','r']

def count_neurons(line):
	line=line.split(',')
	return int(line[0].split()[2])
def length(line):
	line=line.split(',')
	return int(line[1].split()[2])
def fire_times(line):
	senders=[]
	times=[]
	line=line.split(',')
	N_fired=int(line[0].split()[2])
	for i in range(N_fired):
		senders.append(int(line[2+2*i].split()[2])-1)
		times.append(int(line[3+2*i].split()[2]))
	return np.array(times),np.array(senders)

def links(line):
	N_fired=int(line.split(',')[0].split()[2])
	line=line.split('links')
	line=line[1:]
	pre,post,delay,layer=[],[],[],[]
	for i in line:
		i=i.split('=')[1]
		idxleft=i.index('[')
		idxright=i.index(']')
		i=i[idxleft+1:idxright]
		container=i.split(',')

		pre.append(int(container[0])-1)
		post.append(int(container[1])-1)
		delay.append(int(container[2]))
		layer.append(int(container[3])-1)
	return pre,post,delay,layer

def strip_graph(line):
	N = count_neurons(line)
	L = length(line)
	senders, times = fire_times(line)
	pre, post, delay, layer = links(line)
	return N, L, senders, times, pre, post, delay, layer

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

