import argparse,os
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str)
parser.add_argument('-si', type=str)
parser.add_argument('-n', type=str)
parser.add_argument('-sn', type=str)
parser.add_argument('-o', type=str)

args = parser.parse_args()

def mem_plot(data,c):
    id=data[:,0]
    t=data[:,1]
    v=data[:,2]
    u = data[:, 3]
    print v[(id==1)&(t<15)]
    for i,idx in enumerate(np.unique(id)):
        print i,idx

        plt.subplot(2, 2,i+1)
        plt.plot(t[id==idx],v[id==idx],c,linewidth=0.2)
        plt.plot(t[id==idx],u[id==idx],c,linewidth=0.2)

        plt.xlim([900, 1200])
        plt.ylim([-100, 150])

def spk_plot(data,c):
    id=data[:,0]
    t=data[:,1]
    plt.plot(t,id,c)

    plt.xlim([990, 1200])



izh_data=np.loadtxt(args.i)
nest_data=np.loadtxt(args.n)
mem_plot(izh_data,'r')
mem_plot(nest_data,'b')
izh_data=np.loadtxt(args.si)
nest_data=np.loadtxt(args.sn)

red_patch = mpatches.Patch(color='red', label='Izhikevic Model')
blue_patch = mpatches.Patch(color='blue', label='NEST Model')

plt.legend(handles=[red_patch,blue_patch])


plt.savefig(os.path.join(args.o,'membrane_potential_comparison.pdf'))

plt.close()

spk_plot(izh_data,'r.')
spk_plot(nest_data,'b.')

red_patch = mpatches.Patch(color='red', label='Izhikevic Model')
blue_patch = mpatches.Patch(color='blue', label='NEST Model')

plt.legend(handles=[red_patch,blue_patch])


plt.savefig(os.path.join(args.o,'spikes_comparison.pdf'))