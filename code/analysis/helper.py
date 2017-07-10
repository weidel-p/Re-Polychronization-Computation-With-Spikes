import numpy as np
import matplotlib.pyplot as plt
import json
import yaml
import os

def weight_dist(data,c):
    weight=[i['weight'] for i in data]
    delay = [i['delay'] for i in data]
    pre = [i['pre'] for i in data]
    post = [i['post'] for i in data]
    ex_ex_w = [i['weight'] for i in data if (i['pre']<800 and i['post']<800)]
    ex_in_w = [i['weight'] for i in data if (i['pre']<800 and i['post']>=800)]
    in_ex_w = [i['weight'] for i in data if (i['pre']>=800 and i['post']<800)]
    all_w=weight
    return all_w,ex_ex_w,ex_in_w,in_ex_w

def weight_dist(data,c):
    weight=[i['weight'] for i in data]
    delay =np.array( [i['delay'] for i in data])
    pre = np.array([i['pre'] for i in data])
    post = np.array([i['post'] for i in data])
    ex_ex_w = [i['weight'] for i in data if (i['pre']<800 and i['post']<800)]
    ex_in_w = [i['weight'] for i in data if (i['pre']<800 and i['post']>=800)]
    in_ex_w = [i['weight'] for i in data if (i['pre']>=800 and i['post']<800)]
    all_w=weight
    outdegree=[np.sort(delay[pre==i]).size for i in pre if i <800]
    print outdegree[:3]
    outdegree=[np.sort(delay[post==i]).size for i in post if i<800]
    print outdegree[:3]

    return all_w,ex_ex_w,ex_in_w,in_ex_w


def delay_dist(data,c):
    weight=[i['weight'] for i in data]
    delay = [i['delay'] for i in data]
    pre = [i['pre'] for i in data]
    post = [i['post'] for i in data]


    ex_ex_d = [i['delay'] for i in data if (i['pre']<800 and i['post']<800)]
    ex_in_d = [i['delay'] for i in data if (i['pre']<800 and i['post']>=800)]
    in_ex_d = [i['delay'] for i in data if (i['pre']>=800 and i['post']<800)]
    all_d=delay


    return all_d,ex_ex_d, ex_in_d, in_ex_d


def parse_config(config_file):
    with open(config_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    base = os.path.basename(config_file)
    base_and_extless=os.path.splitext(base)[0]
    print base_and_extless
    cfg['simulation-params']['data-prefix']=base_and_extless
    print cfg

    return cfg


def match_pattern(times, senders, t, group, threshold=0.4):
    count = 1
    adjusted_time = times - t
    for i, neuron in enumerate(group['senders']):
        t_window = adjusted_time - group['times'][i]
        p0 = abs(t_window) <= 2.
        target = senders[p0]
        if neuron in target:
            count += 1
    if group['N'] * threshold <= count * 1.0:
        return True, count * 1.0 / group['N']
    else:
        return False, count * 1.0 / group['N']


def bin_pop_rate(times, senders, binwidth=1.):
    t_min = np.min(times)
    t_max = np.max(times)
    N_senders = len(np.unique(senders))
    rate, bin_edges = np.histogram(times, np.arange(t_min, t_max, binwidth))
    return rate * 1000 / (N_senders * binwidth), bin_edges[:-1]
def split_in_ex(times, senders):
    exc_sender = senders[senders <= 800]
    exc_times = times[senders <= 800]
    inh_sender = senders[senders > 800]
    inh_times = times[senders > 800]
    return exc_times,exc_sender,inh_times,inh_sender



def calc_specgram(time, rate, NFFT=1024, noverlap=900):
    Pxx, freqs, bins, im = plt.specgram(rate, NFFT=NFFT, Fs=1000. / (time[2] - time[1]), noverlap=noverlap)
    return freqs, Pxx, bins


def load_json(fname):
    f = open(fname, 'r')
    data = json.load(f)
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
        if 'bitwise' in filename:
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
