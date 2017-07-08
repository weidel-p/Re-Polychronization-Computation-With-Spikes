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
import plot_helper as phf
parser = argparse.ArgumentParser()
parser.add_argument('-g','--groupfile', type=str)
parser.add_argument('-o','--outfolder', type=str)


args = parser.parse_args()



groups = hf.read_group_file(args.groupfile)
print 'loading group data done'
print 'found {} groups'.format(len(groups))

outfolder=args.outfolder
outname='plot_8.png'
phf.plot_8(groups,os.path.join(outfolder,outname))
print 'plot 8 done'
fig=plt.figure()
ax=fig.add_subplot(111)
if len(groups)>1:
    phf.plot_group(groups[1], ax, LP=False, numbers=False)
plt.savefig(os.path.join(outfolder,'plot_7.png'))
print 'plot 7 done'

