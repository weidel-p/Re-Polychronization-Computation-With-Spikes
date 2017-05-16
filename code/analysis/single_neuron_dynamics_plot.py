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
    for i in np.unique(id):
        plt.plot(t[id==i],v[id==i]+(i-1)*40,c,linewidth=0.1)
    plt.xlim([0,500])

izh_data=np.loadtxt(args.i)
nest_data=np.loadtxt(args.n)
print izh_data,nest_data
mem_plot(izh_data,'r')
mem_plot(nest_data,'b')
red_patch = mpatches.Patch(color='red', label='Izhikevic Model')
blue_patch = mpatches.Patch(color='blue', label='NEST Model')

plt.legend(handles=[red_patch,blue_patch])


plt.savefig(args.o)