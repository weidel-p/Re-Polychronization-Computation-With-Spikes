import argparse
import numpy as np
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import helper as hf

parser = argparse.ArgumentParser()
parser.add_argument('-c', type=str)
parser.add_argument('-wo', type=str)
parser.add_argument('-do', type=str)


args = parser.parse_args()



connectivity=hf.load_json(args.c)
all_w,ex_ex_w,ex_in_w,in_ex_w=hf.weight_dist(connectivity,'r')

blue_patch = mpatches.Patch(color='blue', label='NEST Model')



plt.hist(all_w, bins=np.linspace(-0.5, 10.5, 11), histtype='step', color='k')
plt.title('all weights')
plt.hist(ex_ex_w, bins=np.linspace(-0.5, 10.5, 11), histtype='step', color='r')
plt.title('ex-ex')
plt.hist(ex_in_w, bins=np.linspace(-0.5, 10.5, 11), histtype='step', color='m')
plt.title('ex-in')
plt.hist(in_ex_w, bins=np.linspace(-0.5, 10.5, 11), histtype='step', color='b')
plt.title('in_ex')

plt.savefig(args.wo)
plt.close()


all_d,ex_ex_d, ex_in_d, in_ex_d=hf.delay_dist(connectivity,'b')

plt.hist(all_d, bins=np.linspace(-0.5, 20.5, 22), histtype='step', color='k')
plt.title('all weights')

plt.hist(ex_ex_d, bins=np.linspace(-0.5, 20.5, 22), histtype='step', color='r')
plt.title('ex-ex')

plt.hist(ex_in_d, bins=np.linspace(-0.5, 20.5, 22), histtype='step', color='m')
plt.title('ex-in')

plt.hist(in_ex_d, bins=np.linspace(-0.5, 20.5, 22), histtype='step', color='b')
plt.title('in-ex')

plt.savefig(args.do)
plt.close()