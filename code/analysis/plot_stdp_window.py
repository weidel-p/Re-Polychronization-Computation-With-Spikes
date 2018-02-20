import numpy as np
import sys
import helper
import json
import argparse
import pylab as plt

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', nargs='+', type=str)
parser.add_argument('-o', '--output', type=str)

args = parser.parse_args()

plt.figure(figsize=[16,10])

for i in args.input:
    with open(i, 'r+') as f:
        data = json.load(f)
        if 'bitwise' in data['label'] or 'naive' in data['label']:
        #if "additive_stdp" in data['label'] or 'quali' in data['label'] or 'bitwise' in data['label'] or 'naive' in data['label'] or 'multi' in data['label']:
            plt.plot(data['dt'], data['dw'], label=data['label'])

plt.axhline(0, color='k', linestyle='--')
plt.axvline(0, color='k', linestyle='--')
plt.legend()
plt.xlabel("dt")
plt.ylabel("dw")
plt.savefig(args.output)


