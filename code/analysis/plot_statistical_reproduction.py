import numpy as np
import json
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.gridspec as gridspec
import pylab as plt
import helper as hf
import plot_helper as phf
import argparse
import matplotlib.patches as mpatches
import mpl_toolkits.axes_grid.inset_locator



parser = argparse.ArgumentParser()
parser.add_argument('-ss','--statistical_spikefile', type=str)
parser.add_argument('-bs','--bitwise_spikefile', type=str)

parser.add_argument('-sw','--statistical_weightfile', type=str)
parser.add_argument('-bw','--bitwise_weightfile', type=str)

parser.add_argument('-fn','--filename', type=str)

import seaborn as sns

flatui = [ sns.xkcd_rgb["denim blue"],sns.xkcd_rgb["medium green"],sns.xkcd_rgb["pale red"]]
plt.figure()
current_palette = sns.color_palette(flatui)
sns.palplot(current_palette)
sns.set_palette(current_palette)
plt.savefig('palette.png')
plt.close()
args = parser.parse_args()

excolor='C0'
incolor='C1'


statistical_spikefile = args.statistical_spikefile
statistical_times, statistical_senders = hf.read_spikefile(statistical_spikefile)
bitwise_spikefile = args.bitwise_spikefile
bitwise_times, bitwise_senders = hf.read_spikefile(bitwise_spikefile)

statistical_weights = hf.read_weightfile(args.statistical_weightfile)
bitwise_weights = hf.read_weightfile(args.bitwise_weightfile)




fig = plt.figure(figsize=(9, 8))
gs0 = gridspec.GridSpec(2, 2)
gs0.update(left=0.1, right=0.97, top=0.97, bottom=0.06, hspace=0.15)

gs1 = gridspec.GridSpecFromSubplotSpec(7, 1, subplot_spec=gs0[0,:])

ax01 = plt.subplot(gs1[:5, 0])
ax02 = plt.subplot(gs1[5:, 0])

phf.plot_raster_rate(statistical_times,statistical_senders,ax01,ax02,incolor=incolor,excolor=excolor)
ax1=plt.subplot(gs0[1,0])
ax2=plt.subplot(gs0[1,1])


phf.plot_weights(statistical_weights,ax1,'k',ylim=[150,55000],alpha=0.5)
phf.plot_weights(bitwise_weights,ax1,'k',ylim=[150,55000],alpha=0.3)



axin1 = mpl_toolkits.axes_grid.inset_locator.inset_axes(ax1,
                                                        width="45   %",  # width = 30% of parent_bbox
                                                        height=1.5,  # height : 1 inch
                                                        borderpad=1.5

                                                        )

boxplot_kwargs = dict(positions=range(4),
                      bootstrap=1000,
                      showmeans=True,
                      labels=['Inh','Exc','Inh','Exc']
                      )
statistical_exc_times, statistical_exc_sender, statistical_inh_times, statistical_inh_sender = hf.split_in_ex(statistical_times, statistical_senders)
statistical_inh_rate, statistical_inh_bins = hf.bin_pop_rate(statistical_inh_times, statistical_inh_sender, 1.)
statistical_exc_rate, statistical_exc_bins = hf.bin_pop_rate(statistical_exc_times, statistical_exc_sender, 1.)
bitwise_exc_times, bitwise_exc_sender, bitwise_inh_times, bitwise_inh_sender = hf.split_in_ex(bitwise_times, bitwise_senders)
bitwise_inh_rate, bitwise_inh_bins = hf.bin_pop_rate(bitwise_inh_times, bitwise_inh_sender, 1.)
bitwise_exc_rate, bitwise_exc_bins = hf.bin_pop_rate(bitwise_exc_times, bitwise_exc_sender, 1.)

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)



bpexc = axin1.boxplot([bitwise_exc_rate,statistical_exc_rate],
                      positions=np.array(range(2))*2.0-0.4,
                      sym='',
                      widths=0.6,
                      labels=['original','NEST'])
bpinh = axin1.boxplot([bitwise_inh_rate,statistical_inh_rate],
                      positions=np.array(range(2))*2.0+0.4,
                      sym='',
                      widths=0.6,
                      labels=['original','NEST'])
set_box_color(bpexc, excolor) # colors are from http://colorbrewer2.org/
set_box_color(bpinh, incolor)
axin1.set_xlim([-1,3])
axin1.set_yticks([0,25,50,75])

phf.plot_psd(bitwise_times, bitwise_senders,ax2,excolor='C2',incolor=None)
phf.plot_psd(statistical_times, statistical_senders,ax2,excolor=excolor,incolor=None)
NEST = plt.Line2D((0, 1), (0, 0), color=excolor, linestyle='-')
original = plt.Line2D((0, 1), (0, 0), color='C2', linestyle='-')

# Create legend from custom artist/label lists
ax2.legend([NEST,original],
            ['NEST','original'], loc=1,
           prop={'size': 12})

for ax,letter in [(ax1,'B'),(ax2,'C')]:
    ax.annotate(letter, xy=(-0.08, 0.99), xycoords='axes fraction', fontsize=20,
                horizontalalignment='left', verticalalignment='top', annotation_clip=False)
ax01.annotate('A', xy=(-0.03, 0.99), xycoords='axes fraction', fontsize=20,
            horizontalalignment='left', verticalalignment='top', annotation_clip=False)

plt.savefig(args.filename)
