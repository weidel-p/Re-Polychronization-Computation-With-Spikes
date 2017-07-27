import argparse
import numpy as np
import os,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import helper as hf
import plot_helper as phf
parser = argparse.ArgumentParser()
parser.add_argument("-sl",'--spikelist', help="list of spike files", nargs="+")

parser.add_argument("-cl",'--connectivitylist', help="list of connectivity files", nargs="+")

parser.add_argument('-o', type=str)

args = parser.parse_args()

fig=plt.figure(figsize=(15,6))
gs0 = gridspec.GridSpec(1, 3)
gs0.update(left=0.05, right=0.97, top=0.97, bottom=0.1, hspace=0.15)
ax=plt.subplot(gs0[0,0])
ax_lowdelay=plt.subplot(gs0[0,1])
ax_highdelay=plt.subplot(gs0[0,2])

for file in args.spikelist:
    times, senders = hf.read_spikefile(file)

    phf.plot_psd(times,senders,ax)


low_delay=False
high_delay=False
for connectivity,spikes in zip(range(len(args.spikelist)),args.connectivitylist,args.spikelist):
    connectivity = hf.load_json(connectivity)
    all_w, ex_ex_w, ex_in_w, in_ex_w = hf.weight_dist(connectivity, 'r')
    all_d, ex_ex_d, ex_in_d, in_ex_d = hf.delay_dist(connectivity, 'b')

    weights,delays,counts=hf.weight_delay_histograms(ex_ex_w + ex_in_w, ex_ex_d+ ex_in_d)
    idx=np.where(counts==np.max(counts))
    print delays[idx[0],idx[1]],weights[idx[0],idx[1]],counts[idx[0],idx[1]]
    if delays[idx[0],idx[1]]>15:
        color='k'

        if not high_delay:
            phf.plot_2D_weights(weights, delays, counts, ax_highdelay)
            high_delay = True

    if delays[idx[0], idx[1]] < 15 and not low_delay:
        color='b'

        if not high_delay:
            phf.plot_2D_weights(weights, delays, counts, ax_lowdelay)
            low_delay = True

    times, senders = hf.read_spikefile(spikes)
    phf.plot_psd(times, senders, ax,incolor=color,excolor=color)

plt.savefig(args.o)

