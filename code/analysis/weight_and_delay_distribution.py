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

fig = plt.figure(figsize=(18, 6))
plt.subplot(1,3,1)
plt.hist(all_w, bins=np.linspace(-0.5, 10.5, 11), histtype='step', color='k')
plt.title('all weights')
plt.hist(ex_ex_w, bins=np.linspace(-0.5, 10.5, 11), histtype='step', color='r')
plt.title('ex-ex')
plt.hist(ex_in_w, bins=np.linspace(-0.5, 10.5, 11), histtype='step', color='m')
plt.title('ex-in')
plt.hist(in_ex_w, bins=np.linspace(-0.5, 10.5, 11), histtype='step', color='b')
plt.title('in_ex')


all_d,ex_ex_d, ex_in_d, in_ex_d=hf.delay_dist(connectivity,'b')
plt.subplot(1,3,3)

plt.hist(all_d, bins=np.linspace(-0.5, 20.5, 22), histtype='step', color='k')
plt.title('all weights')

plt.hist(ex_ex_d, bins=np.linspace(-0.5, 20.5, 22), histtype='step', color='r')
plt.title('ex-ex')

plt.hist(ex_in_d, bins=np.linspace(-0.5, 20.5, 22), histtype='step', color='m')
plt.title('ex-in')

plt.hist(in_ex_d, bins=np.linspace(-0.5, 20.5, 22), histtype='step', color='b')
plt.title('in-ex')
plt.subplot(1,3,2)
print np.min(ex_in_w+ex_ex_w),np.max(ex_in_w+ex_ex_w)
print np.min(ex_in_d+ex_ex_d),np.max(ex_in_d+ex_ex_d)

H, xedges, yedges = np.histogram2d(ex_ex_w,ex_ex_d, bins= (np.linspace(-0.5, 10.5, 12),np.linspace(0.5, 20.5, 21)))
X, Y = np.meshgrid(xedges[:-1]+0.5*(xedges[1]-xedges[0]),yedges[:-1]+0.5*(yedges[1]-yedges[0]) )
print X.shape,Y.shape,X,Y
plt.pcolormesh( (H.T))
plt.colorbar()

plt.savefig(args.wo)
plt.close()
