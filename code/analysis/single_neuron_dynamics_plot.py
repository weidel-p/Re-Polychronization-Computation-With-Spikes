import argparse
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str)
parser.add_argument('-n', type=str)
parser.add_argument('-o', type=str)

args = parser.parse_args()

def mem_plot(data,c):
    id=data[:,0]
    t=data[:,1]
    v=data[:,2]
    u = data[:, 3]
    print v[(id==1)&(t<15)]
    for i in np.unique(id):
        if i>10:
            k=i-996
        else:
            k=i

        plt.subplot(2, 2,k)
        plt.plot(t[id==i],v[id==i],c,linewidth=0.2)
        plt.plot(t[id==i],u[id==i],c,linewidth=0.2)

        plt.xlim([900, 1200])
        plt.ylim([-100, 150])


izh_data=np.loadtxt(args.i)
nest_data=np.loadtxt(args.n)
mem_plot(izh_data,'r')
mem_plot(nest_data,'b')
red_patch = mpatches.Patch(color='red', label='Izhikevic Model')
blue_patch = mpatches.Patch(color='blue', label='NEST Model')

plt.legend(handles=[red_patch,blue_patch])


plt.savefig(args.o)