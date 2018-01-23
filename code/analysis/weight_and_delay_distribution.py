import argparse
import numpy as np
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import helper as hf
import plot_helper as phf
parser = argparse.ArgumentParser()
parser.add_argument('-c', type=str)
parser.add_argument('-o', type=str)


args = parser.parse_args()


# start with a rectangular Figure
fig = plt.figure(figsize=(8, 8))

N = 5
gs0 = gridspec.GridSpec(N, N)
gs0.update(left=0.1, right=0.97, top=0.97, bottom=0.06, hspace=0.15)

ax2Dhist = plt.subplot(gs0[1:, :N - 1])

axHistx = plt.subplot(gs0[0, :N - 1])
axHisty = plt.subplot(gs0[1:, N - 1])


connectivity = hf.load_json(args.c)
all_w, ex_ex_w, ex_in_w = hf.conn_dist(connectivity, 'weight')
all_d, ex_ex_d, ex_in_d = hf.conn_dist(connectivity, 'delay')


weights_ex_in, delays_ex_in, counts_ex_in = hf.weight_delay_histograms(ex_in_w, ex_in_d)
weights_ex_ex, delays_ex_ex, counts_ex_ex = hf.weight_delay_histograms(ex_ex_w, ex_ex_d)
weights, delays, counts = hf.weight_delay_histograms(ex_ex_w + ex_in_w, ex_ex_d + ex_in_d)

phf.plot_2D_weights(weights, delays, counts, ax2Dhist)


xhist = np.mean(counts, axis=0)
yhist = np.mean(counts, axis=1)
xhist_ex_in = np.mean(counts_ex_in, axis=0)
yhist_ex_in = np.mean(counts_ex_in, axis=1)
xhist_ex_ex = np.mean(counts_ex_ex, axis=0)
yhist_ex_ex = np.mean(counts_ex_ex, axis=1)

yedges_mean, xedges_mean = np.mean(delays, axis=1)[1:] - 0.5, np.mean(weights, axis=0)[:-1] + 0.5
print xedges_mean, yedges_mean
print xhist, yhist
print xedges_mean.shape, yedges_mean.shape

print xhist.shape, yhist.shape
axHistx.bar(xedges_mean, xhist, color='k', orientation='vertical')
axHistx.bar(xedges_mean, xhist, color='m', orientation='vertical')

axHisty.bar(yhist, yedges_mean, color='k', orientation='vertical')
axHistx.bar(xedges_mean, xhist_ex_ex, color='r', orientation='vertical')
axHisty.bar(yhist_ex_ex, yedges_mean, color='r', orientation='vertical')

axHistx.bar(xedges_mean, xhist_ex_in, color='b', orientation='vertical')
axHisty.bar(yhist_ex_in, yedges_mean, color='b', orientation='vertical')

axHistx.set_xticks([])
axHisty.set_xticks([])
axHistx.set_yticks([])
axHisty.set_yticks([])


axHistx.set_xlim([0, 11])
axHisty.set_ylim([1, 20])

plt.savefig(args.o)
plt.close()
