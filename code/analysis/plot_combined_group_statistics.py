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
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument('-fn', '--filename', type=str)
parser.add_argument("-gl", help="list of group files", nargs="+")



args = parser.parse_args()
print args.gl
groups=[]
for groupfile in args.gl:
    groups.append(hf.read_group_file(groupfile))
print 'loading group data done'
print 'found {} group files'.format(len(groups))

outname='plot_8.png'
phf.plot_combined_groups_statstics(groups,args.filename)
print 'plot combined 8 done'

