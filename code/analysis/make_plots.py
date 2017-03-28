import numpy as np
import json
import sys
import os
import matplotlib.gridspec as gridspec
import pylab as plt
import helper as hf
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-g','--groupfile', type=str)
parser.add_argument('-s','--spikefile', type=str)
parser.add_argument('-w','--weightfile', type=str)
parser.add_argument('-o','--outfolder', type=str)
parser.add_argument('-p','--prefix', type=str)


args = parser.parse_args()


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

def read_group_file(filename):
    with open(filename, "r") as f:
        if '.json' in filename:
                groups = json.load(f)
        else:
            groups=[]
            for line in f.readlines():
                groups.append(convert_line(line))
    return groups

def get_t_s(group):
    times=[]
    senders=[]
    for i in group['fired']:
        times.append(i['t_fired'])
        senders.append(i['neuron_id'])

    return np.array(times).astype(float),np.array(senders).astype(float)

def read_spikefile(filename):
    if 'spikes.dat' in filename:
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
    return np.array(weights)

def plot_group(group,ax,LP=False,numbers=True):

    N_fired = group['N_fired']
    times, senders = get_t_s(group)
    idx_in = senders > 800
    idx_ex = senders < 800
    ax1 = ax.twinx()

    ax.scatter(times[idx_ex], senders[idx_ex], s=80, facecolors='none', edgecolors='r')
    ax1.scatter(times[idx_in], (senders[idx_in] - 800) * 4, s=80, facecolors='k')

    for link in group['links']:
        if link['post'] < 799:
            post_i = link['post']
        else:
            post_i = (link['post'] - 800) * 4

        ax.plot([times[link['pre'] == senders], times[link['post'] == senders]],
                [link['pre'], post_i], 'k')
        if numbers:
            ax.text(times[link['pre'] == senders] + 1,
                    link['pre'] - 10,
                    s=str(link['pre']),
                    fontsize=12)

            ax.text(times[link['post'] == senders] + 1,
                    post_i - 10,
                    s=str(link['post']),
                    fontsize=12)

    if LP:

        i = len(group['links'])-1
        while group['links'][i]['layer'] >=2:
            i_l=i
            if group['links'][i]['post'] < 799:
                post_i = group['links'][i]['post']
            else:
                post_i = (group['links'][i]['post'] - 800) * 4
            ax.plot([times[group['links'][i]['pre'] == senders],
                     times[group['links'][i]['post'] == senders]], [group['links'][i]['pre'],
                                                  post_i], 'k', linewidth=4,alpha=0.5)
            if group['links'][i]['layer'] == group['L_max']:
                ax.text(times[group['links'][i]['layer'] == senders] - 20,
                        post_i + 20,
                        s='longest path',
                        fontsize=11)
            for j in range(len(group['links'])):
                if group['links'][j]['post']==group['links'][i]['pre']:
                    i_l=j
            if group['links'][i]['layer'] ==2:
                break
            i=i_l



    ax.set_ylim(-20, 820)
    ax1.set_ylim(-20, 820)

    ax.set_yticks([0, 400, 800])

    ax1.set_yticks([0, 800])
    ax1.set_yticklabels([800, 1000])

    ax.set_xlim(np.min(times) - 10, np.max(times) + 10)
    ax1.set_xlim(np.min(times) - 10, np.max(times) + 10)


def plot_8(group_data,outname):
    fig = plt.figure("plot 8")
    ax0 = fig.add_subplot(221)
    ax1 = fig.add_subplot(222)
    ax2 = fig.add_subplot(223)
    ax3 = fig.add_subplot(224)
    
    N_list=[]
    L_list=[]
    T_list=[]
    for i, g in enumerate(group_data):
        times, senders = get_t_s(g)

        N_list.append(int(g["N_fired"]))
    
        T_list.append(max(times)) # time span
    
        L_list.append(int(g["L_max"])) # longest path

    ax1.hist(N_list, 100)
    ax1.set_title('# of neurons')
    ax2.hist(T_list, 100)
    ax2.set_title('time span[ms]')
    ax3.hist(L_list, 30)
    ax3.set_title('length of longest path')

    plot_group(g, ax0, LP=True, numbers=False)

    plt.savefig(outname)

def plot_5(times,senders,outname):
    fig = plt.figure(figsize=(9, 12))
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    for t, ax in [(0, ax1), (100, ax2), (3600, ax3)]:

        idx = (times > (t*1000)) & (times < (t*1000 + 1000.))
        sub_times = times[idx]
        sub_senders = senders[idx]
        ax.plot(sub_times, sub_senders, 'k.')
        ax.set_xticks(np.min(times) + np.linspace(0, 1000, 6, endpoint=True))
        ax.set_xticklabels(np.linspace(0, 1000, 6, endpoint=True).astype(int))
        ax.set_xlim([np.min(times), np.min(times) + 1000])
        ax.set_ylabel('#Neuron')
        ax.set_title('sec = {}'.format(int(t)), loc='left')
    ax3.set_xlabel('Time[ms]')
    plt.savefig(outname)
    plt.close()


def plot_specgram(times,senders,weights,outname):
    exc_sender = senders[senders < 800]
    exc_times = times[senders < 800]
    inh_sender = senders[senders > 800]
    inh_times = times[senders > 800]
    inh_rate, inh_bins = hf.bin_pop_rate(inh_times, inh_sender, 1.)
    exc_rate, exc_bins = hf.bin_pop_rate(exc_times, exc_sender, 1.)
    freqs, Pxx, bins=hf.calc_specgram(exc_bins, exc_rate-np.mean(exc_rate), NFFT=512, noverlap=500)

    fig = plt.figure(figsize=(9, 8))
    gs2 = gridspec.GridSpec(2, 2)
    gs2.update(left=0.1, right=0.97, top=0.97, bottom=0.06, hspace=0.15)

    ax0 = plt.subplot(gs2[0,0])
    ax1 = plt.subplot(gs2[0,1])
    ax2 = plt.subplot(gs2[1,0])
    ax3 = plt.subplot(gs2[1,1])


    idx = (times > (np.min(times))) & ((times < (np.min(times)+5000.) ))
    ax0.plot(times[idx],senders[idx],'k.',markersize=2)
    ax0.set_xlim([np.min(times),np.min(times)+5000])
    ax0.set_ylim([0, 1000])
    ax0.set_xticks(np.linspace(np.min(times),np.min(times)+5000, num=6, endpoint=True))
    ax0.set_xticklabels(np.linspace(0, 5, num=6,endpoint=True))
    ax0.set_xlabel('Time [s]')
    ax0.set_ylabel('#Neuron')
    ax0.set_title('sec = {}'.format(int(np.min(times)/1000)), loc='left')

    ax1.plot(inh_bins, inh_rate, 'r')
    ax1.plot(exc_bins, exc_rate, 'k')
    ax1.set_xlim([np.min(inh_bins),np.max(inh_bins)])
    ax1.set_xticks(np.linspace(np.min(inh_bins), np.max(inh_bins),3,endpoint=True))
    ax1.set_xticklabels(np.linspace(np.min(inh_bins), np.max(inh_bins), 3, endpoint=True).astype(int)/1000)

    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Population averaged firing rate [spk/s]')

    ax2.hist(weights, bins=20, normed=True)
    ax2.set_ylim([0., 1.4])
    ax2.set_xlim([0.,10.])
    ax2.set_xlabel('Synaptic weight [mV]')
    ax2.set_ylabel('normed count')

    ax3.pcolormesh(bins,freqs,Pxx)
    ax3.set_ylabel('Frequency [Hz]')
    ax3.set_xlabel('Time [s]')
    plt.savefig(outname)
    plt.close()

groups = read_group_file(args.groupfile)
spikefile=args.spikefile
times,senders=read_spikefile(spikefile)
weights=read_weightfile(args.weightfile)
outfolder=args.outfolder
outname=args.prefix+'_plot_8.pdf'
plot_8(groups,os.path.join(outfolder,outname))

fig=plt.figure()
ax=fig.add_subplot(111)
plot_group(groups[1], ax, LP=False, numbers=True)
plt.savefig(os.path.join(outfolder,args.prefix+'_plot_7.pdf'))


plot_5(times,senders,os.path.join(outfolder,args.prefix+'_plot_5.pdf'))

outname=os.path.join(outfolder,args.prefix+'_dynamic_measures.pdf')
plot_specgram(times,senders,weights,outname)