import argparse
import numpy as np
import os,sys
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import mpl_toolkits.axes_grid.inset_locator
import json
import seaborn as sns
import scipy.stats as stat


#sns.set_palette(sns.light_palette("blue"))
parser = argparse.ArgumentParser()
parser.add_argument("-s", '--spikefile', help="spike file", type=str)
parser.add_argument("-g", '--groupfile',help="group file", type=str)
parser.add_argument("-c", '--connectivityfile', help="connectivity files", type=str)

parser.add_argument('-o','--outname', type=str)
args = parser.parse_args()
def save_json(fname,json_data):
    with open(fname, "w") as f:
        json.dump(json_data, f)

def read_group_file(filename):
    with open(filename, "r") as f:
       groups = json.load(f)

    return groups

def get_t_s(group):
    '''

    Parameters
    ----------
    group: group in format as retunred by original algorithm

    Returns
    times: array of spike times
    senders: array of neuron ids ordered to match times
    -------

    '''
    times=[]
    senders=[]
    for i in group['fired']:
        times.append(i['t_fired'])
        senders.append(i['neuron_id'])

    return np.array(times).astype(float),np.array(senders).astype(float)
def format_spiketrains(times,senders):
    '''

    Parameters
    ----------
    times   : array of float
            spike times
    senders : array of float
            id corresponding to spike times

    Returns
    spiketrains: dictionary
        dictionary of spiketrains,
        keys are ids
        correspondint items are spike times of that id
    -------

    '''
    spiketrains=dict()
    for id in np.unique(senders):
        spiketrains[id-1]=times[senders==id].tolist()
    return spiketrains

def get_occurances_in_group(groups):
    '''

    Parameters
    ----------
    groups : list of dict
        group list as returned by jsonified groups from original algorithm

    Returns
    id    : list of int
            ist of neuron id sorted
    count : list of int
            number of occurances in groups
            matched to sort in id
    -------

    '''
    all_occurances=[]
    for group in groups:
        all_occurances+=np.unique(get_t_s(group)[1]).tolist()
    id,count=np.unique(np.array(all_occurances).flatten(),return_counts=True)
    return id,count
def split_exc_and_inh(id,count):
    '''

    Parameters
    ----------
    id    : list of int
            list of neuron id sorted
    count : list of int
            number of occurances in groups
            matched to sort in id

    Returns
    exc_id   : list of int
               list of neuron id sorted and split by excitatory i.e. ids below 800
    exc_count:
               number of occurances in groups
               matched to sort in exc_id
    inh_id   :
               list of neuron id sorted and split by inhibitory i.e. ids above 800

    inh_count:
               number of occurances in groups
               matched to sort in inh_id

    -------

    '''
    exc_id=id[id<800]
    exc_count=count[id<800]
    inh_id=id[id>=800]
    inh_count=count[id>=800]
    return exc_id,exc_count,inh_id,inh_count
def sort_by_occurance(id,count,high=True):
    '''
    Parameters
    ----------
    id    : list of int
            list of neuron id sorted
    count : list of int
            number of occurances in groups
            matched to sort in id
    high  : boolean
            if true order by high occurance if false by low
    Returns
    -------
    sorted_id    : list of int
            list of neuron id sorted by occurance
    sorted_count : list of int
            number of occurances in groups
            matched to sort in sorted_id

    '''
    idx = np.argsort(count)

    if not high:
        idx=idx[::-1]
    sorted_id=id[idx]
    sorted_count=count[idx]
    return sorted_id,sorted_count



def select_spiketrains(exc_id,inh_id,spk_trains,N_exc=100,N_inh=25):
    '''

    Parameters
    ----------
    exc_id   : list of int
               list of neuron id sorted by occurance and split by excitatory i.e. ids below 800
    exc_count:list of int
               number of occurances in groups
               matched to sort in exc_id
    inh_id   :list of int
               list of neuron id sorted by occurance and split by inhibitory i.e. ids above 800
    inh_count:list of int
               number of occurances in groups
               matched to sort in inh_id
    spk_trains: list of dict
               spike trains from simulation spk_trains[id] are the spike times
    N_exc: int
            number of exc units to select
    N_inh: int
            number of inh units to select

    Returns
    -------
    selected_spk_trains: dict
                returns dict of spiketrains for

    '''
    selected_id=inh_id[:N_inh].tolist()+exc_id[:N_exc].tolist()
    selected_spiketrains=dict()
    for id in selected_id:
        selected_spiketrains.update({id:spk_trains[id]})

    return selected_spiketrains


spikefile = args.spikefile
spikes = np.loadtxt(spikefile)
times = spikes[:, 1]
senders = spikes[:, 0]
spiketrains = format_spiketrains(times,senders)
groups = read_group_file(args.groupfile)
#incase a neuron fires twice in a group
id,count=get_occurances_in_group(groups)
exc_id,exc_count,inh_id,inh_count=split_exc_and_inh(id,count)

unsorted=select_spiketrains(exc_id,inh_id,spk_trains=spiketrains)

exc_id,exc_count=sort_by_occurance(exc_id,exc_count,True)
inh_id,inh_count=sort_by_occurance(inh_id,inh_count,True)
high_sorted=select_spiketrains(exc_id,inh_id,spk_trains=spiketrains)

exc_id,exc_count=sort_by_occurance(exc_id,exc_count,False)
inh_id,inh_count=sort_by_occurance(inh_id,inh_count,False)
low_sorted=select_spiketrains(exc_id,inh_id,spk_trains=spiketrains)



save_json('unsorted_spk_trains.json',unsorted)
save_json('high_sorted_spk_trains.json',high_sorted)
save_json('low_sorted_spk_trains.json',low_sorted)
