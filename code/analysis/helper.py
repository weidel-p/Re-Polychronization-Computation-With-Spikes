import numpy as np
import matplotlib.pyplot as plt
import json
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

def load_json(fname):
    f=open(fname,'r')
    data=json.load(f)
    return data


def convert_line(line):
    split_line = line.split(',')
    N,L=split_line.pop(0).split() # Number of neurons in group and max Layer in the first line
    fired=[] # save all time/sender pairs of the group, these items are in pairs of two
    while len(split_line[0].split())<4:
        s,t=split_line.pop(0).split()
        fired.append({'neuron_id':int(s),'t_fired':int(t)})
    links=[]
    while len(split_line[0].split()) == 4: #save all links, writte nin pairs of 4, pre post delay and layer
        pr,po,d,l = split_line.pop(0).split()
        links.append({'pre':int(pr),'post':int(po),'delay':int(d),'layer':int(l)})

    group=dict(
        N_fired=N,
        L_max=L,
        fired=fired,
        links=links
    )
    return group

def get_t_s(group):
    times=[]
    senders=[]
    for i in group['fired']:
        times.append(i['t_fired'])
        senders.append(i['neuron_id'])

    return np.array(times).astype(float),np.array(senders).astype(float)

def read_spikefile(filename):
    if '.dat' in filename:
        if 'single_stim' in filename:
            spikes = np.loadtxt(filename)
            times = spikes[:, 1]
            senders = spikes[:, 0]

        else:
            spikes=np.loadtxt(filename)
            times=spikes[:,0]
            senders=spikes[:,1]
    else:
        spikes = np.loadtxt(filename)
        times = spikes[:,1]
        senders = spikes[:, 0]
    return times,senders
def read_weightfile(filename):
    with open(filename, "r") as f:
        all_data = json.load(f)
    weights=[i['weight'] for i in all_data]
    pre_weight=[i['weight'] for i in all_data if (i['pre']==2 and i['post']<100)]
    print pre_weight
    return np.array(weights)

def read_group_file(filename):
    with open(filename, "r") as f:
        if '.json' in filename:
                groups = json.load(f)
        else:
            groups=[]
            for line in f.readlines():
                groups.append(convert_line(line))
    return groups
