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
import seaborn as sns
matplotlib.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
font = {'family': 'serif', 'size': 18}
plt.rc('font', **font)
plt.rc('legend', **{'fontsize': 16})
flatui = [sns.xkcd_rgb["denim blue"], sns.xkcd_rgb["medium green"], sns.xkcd_rgb["pale red"]]
plt.figure()
current_palette = sns.color_palette(flatui)
sns.palplot(current_palette)
sns.set_palette(current_palette)
plt.savefig('palette.png')
plt.close()

parser = argparse.ArgumentParser()
parser.add_argument('-bs', '--bitwise_spikefile', type=str)
parser.add_argument('-os', '--original_spikefile', type=str)
parser.add_argument('-bmem', '--bitwise_mem_pop_file', type=str)


parser.add_argument('-fn', '--filename', type=str)


args = parser.parse_args()
excolor = 'C0'
incolor = 'C1'

original_spikefile = args.original_spikefile
original_times, original_senders = hf.read_spikefile(original_spikefile)
bitwise_spikefile = args.bitwise_spikefile
bitwise_times, bitwise_senders = hf.read_spikefile(bitwise_spikefile)

bitwise_mem_pop = np.loadtxt(args.bitwise_mem_pop_file)


fig = plt.figure(figsize=(9, 8))
gs0 = gridspec.GridSpec(2, 2)
gs0.update(left=0.1, right=0.97, top=0.97, bottom=0.06, hspace=0.15)

gs1 = gridspec.GridSpecFromSubplotSpec(7, 1, subplot_spec=gs0[0, :])

ax01 = plt.subplot(gs1[:5, 0])
ax02 = plt.subplot(gs1[5:, 0])
phf.plot_raster_rate(bitwise_times, bitwise_senders, ax01, ax02, incolor=incolor, excolor=excolor)

ax2 = plt.subplot(gs0[1, 1])


ax0, ax1 = phf.mem_spk_plot(bitwise_mem_pop, original_times, original_senders,
                            gs0[1, 0], mem_color='k', spk_exc_color=excolor, spk_inh_color=incolor)


phf.plot_psd(bitwise_times, bitwise_senders, ax2, excolor=excolor, incolor=None)

# NEST = plt.Line2D((0, 1), (0, 0), color=excolor, linestyle='-')
# original = plt.Line2D((0, 1), (0, 0), color='C2', linestyle='-')
#
# # Create legend from custom artist/label lists
# ax2.legend([original,NEST],
#             ['NEST','original'], loc=1,
#            prop={'size': 12})

for ax, letter in [(ax0, 'B'), (ax1, 'C'), (ax2, 'D')]:
    ax.annotate(letter, xy=(-0.08, 0.99), xycoords='axes fraction', fontsize=20,
                horizontalalignment='left', verticalalignment='top', annotation_clip=False)
ax01.annotate('A', xy=(-0.03, 0.99), xycoords='axes fraction', fontsize=20,
              horizontalalignment='left', verticalalignment='top', annotation_clip=False)


plt.savefig(args.filename)
