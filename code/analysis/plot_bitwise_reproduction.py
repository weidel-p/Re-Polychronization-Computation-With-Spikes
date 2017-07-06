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
parser.add_argument('-bs','--bitwise_spikefile', type=str)
parser.add_argument('-os','--original_spikefile', type=str)
parser.add_argument('-bmem','--bitwise_mem_pop_file', type=str)



parser.add_argument('-fn','--filename', type=str)


args = parser.parse_args()


original_spikefile = args.original_spikefile
original_times, original_senders = hf.read_spikefile(original_spikefile)
bitwise_spikefile = args.bitwise_spikefile
bitwise_times, bitwise_senders = hf.read_spikefile(bitwise_spikefile)

bitwise_mem_pop = np.loadtxt(args.bitwise_mem_pop_file)




fig = plt.figure(figsize=(9, 8))
gs0 = gridspec.GridSpec(2, 2)
gs0.update(left=0.1, right=0.97, top=0.97, bottom=0.06, hspace=0.15)

gs1 = gridspec.GridSpecFromSubplotSpec(5, 1, subplot_spec=gs0[0,:])

ax01 = plt.subplot(gs1[:4, 0])
ax02 = plt.subplot(gs1[4, 0])
phf.plot_raster_rate(bitwise_times,bitwise_senders,ax01,ax02)

ax2=plt.subplot(gs0[1,1])


phf.mem_spk_plot(bitwise_mem_pop,original_times,original_senders,gs0[1,0])


phf.plot_psd(bitwise_times, bitwise_senders,ax2,incolor='b',excolor='k')

exc = plt.Line2D((0, 1), (0, 0), color='k', linestyle='-')
inh = plt.Line2D((0, 1), (0, 0), color='b', linestyle='-')

# Create legend from custom artist/label lists
ax2.legend([exc,inh],
            ['Exc','Inh'], loc=1,
           prop={'size': 12})


plt.savefig(args.filename)

