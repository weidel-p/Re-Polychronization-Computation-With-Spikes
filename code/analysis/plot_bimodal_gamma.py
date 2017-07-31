import argparse
import numpy as np
import os,sys
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import mpl_toolkits.axes_grid.inset_locator
import helper as hf
import plot_helper as phf
import seaborn as sns
#sns.set_palette(sns.light_palette("blue"))
cmap = sns.light_palette("blue", as_cmap=True)
parser = argparse.ArgumentParser()
parser.add_argument("-sl",'--spikelist', help="list of spike files", nargs="+")

parser.add_argument("-cl",'--connectivitylist', help="list of connectivity files", nargs="+")

parser.add_argument('-o', type=str)

args = parser.parse_args()
gs = gridspec.GridSpec(1,2, wspace=.2)
fig=plt.figure(figsize=(15,6))


gs0 = gridspec.GridSpec(1, 3)
gs0.update(left=0.05, right=0.97, top=0.97, bottom=0.1, hspace=0.15)

ax = plt.subplot(gs0[0, 0])

ax_low = plt.subplot(gs0[0, 1])
ax_high = plt.subplot(gs0[0, 2])
low_delay=0
high_delay=0
for i,connectivity,spikes in zip(range(len(args.spikelist)),args.connectivitylist,args.spikelist):
    connectivity = hf.load_json(connectivity)
    all_w, ex_ex_w, ex_in_w = hf.conn_dist(connectivity, 'weight')
    all_d, ex_ex_d, ex_in_d = hf.conn_dist(connectivity, 'delay')

    weights,delays,counts=hf.weight_delay_histograms(np.append(ex_ex_w,ex_in_w), np.append(ex_ex_d,ex_in_d))
    max_idx=np.argmax(counts)
    idx=np.unravel_index(max_idx, counts.shape)
    print delays[idx[0],idx[1]],weights[idx[0],idx[1]],counts[idx[0],idx[1]]
    delay_of_max=delays[idx[0],idx[1]]
    color = 'C0'
    print weights.shape,delays.shape
    if delay_of_max>15:
        color='C1'
        if high_delay==0:
            phf.plot_2D_weights(weights, delays, counts, ax_high,cmap=cmap)

        high_delay+=1

    if delay_of_max < 15:
        color='C0'
        if low_delay==0:
            phf.plot_2D_weights(weights, delays, counts, ax_low,cmap=cmap)

        low_delay += 1
    times, senders = hf.read_spikefile(spikes)
    phf.plot_psd(times, senders, ax=ax,incolor=None,excolor=color)
    print 'gamma plot {}'.format(i)





axin1 = mpl_toolkits.axes_grid.inset_locator.inset_axes(ax,
                                                        width="45%",  # width = 30% of parent_bbox
                                                        height=1.5,  # height : 1 inch
                                                        borderpad=1.5
                                                        )



labels =  'low gamma','high gamma',
fracs = [high_delay,low_delay]
explode=( 0.1, 0)

plt.pie(fracs, explode=explode, labels=labels,colors=[r'C1',r'C0'],
                autopct='%1.1f%%', shadow=True, startangle=-95)

plt.savefig(args.o)

