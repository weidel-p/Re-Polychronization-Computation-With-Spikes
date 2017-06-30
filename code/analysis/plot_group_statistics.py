import numpy as np
import json
import sys
import os
import matplotlib
matplotlib.use('Agg')
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



groups = hf.read_group_file(args.groupfile)
print 'loading group data done'

spikefile=args.spikefile
times,senders=hf.read_spikefile(spikefile)
print 'loading spikes data done'
weights=hf.read_weightfile(args.weightfile)
print 'loading weight data done'
outfolder=args.outfolder
outname=args.prefix+'_plot_8.pdf'
plot_8(groups,os.path.join(outfolder,outname))
print 'plot 8 done'
fig=plt.figure()
ax=fig.add_subplot(111)
if len(groups)>1:
    plot_group(groups[1], ax, LP=False, numbers=True)
plt.savefig(os.path.join(outfolder,args.prefix+'_plot_7.pdf'))
print 'plot 7 done'

plot_5(times,senders,os.path.join(outfolder,args.prefix+'_plot_5.pdf'))
print 'plot 5 done'
outname=os.path.join(outfolder,args.prefix+'_dynamic_measures.pdf')
plot_specgram(times,senders,weights,outname)
print 'plot specgram done'