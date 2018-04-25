import matplotlib
matplotlib.use('Agg')
import numpy as np
import sys
import helper
import json
import argparse
import pylab as plt
import seaborn as sns 

matplotlib.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})

sns.set_context('paper', font_scale=3.0,
                rc={"lines.linewidth": 1.5})
sns.set_style('whitegrid', {"axes.linewidth": 1.5})



parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', nargs='+', type=str)
parser.add_argument('-o', '--output', type=str)

args = parser.parse_args()

plt.figure(figsize=[16,10])

for i in args.input:
    with open(i, 'r+') as f:
        data = json.load(f)
        if 'quali' in data['label'] or 'bitwise' in data['label'] or 'initial' in data['label'] or 'reso' in data['label']:
            plt.plot(data['dt'], data['dw'], label=data['label'])

plt.axhline(0, color='k', linestyle='--')
plt.axvline(0, color='k', linestyle='--')
plt.legend(loc=2, prop={'size': 12})
plt.xlabel(r"$\Delta t$")
plt.ylabel(r"$\frac{\Delta w}{w}$")
plt.savefig(args.output)


