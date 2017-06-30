import argparse,os
import numpy as np
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str)
parser.add_argument('-si', type=str)
parser.add_argument('-n', type=str)
parser.add_argument('-sn', type=str)
parser.add_argument('-o', type=str)

args = parser.parse_args()

def mem_plot(data,spk,c):
    id=data[:,0]
    t=data[:,1]
    v=data[:,2]
    u = data[:, 3]

    sender=spk[:,0]
    times=spk[:,1]
    t_max=np.max(t)
    for i,idx in enumerate([705,831]):

        plt.subplot(2, 2,i+1)
        plt.plot(t[id==idx],v[id==idx],c,linewidth=0.2)
        plt.plot(t[id==idx],u[id==idx],c,linewidth=0.2)

        plt.plot(times[sender==idx],sender[sender==idx]*0,c+'*',markersize=10)

        plt.xlim([t_max-1000, t_max])
        plt.ylim([-100,100])
        if i>=3:
            break



def spk_plot(data,c):
    id=data[:,0]
    t=data[:,1]
    t_max=np.max(t)

    plt.plot(t,id,c)

    plt.xlim([t_max - 1000., t_max-000])


spk_izh_data=np.loadtxt(args.si)
spk_izh_data[:,0]=spk_izh_data[:,0]+1
spk_nest_data=np.loadtxt(args.sn)

data_len=len(spk_izh_data)
spk_izh_data=spk_izh_data[:data_len]
spk_nest_data=spk_nest_data[:data_len]



izh_data=np.loadtxt(args.i)
izh_data=izh_data[4:]
nest_data=np.loadtxt(args.n)

mem_plot(izh_data,spk_izh_data,'r')
mem_plot(nest_data,spk_nest_data,'b')

# mem_plot(izh_data,0,'r')
# mem_plot(nest_data,0,'b')


red_patch = mpatches.Patch(color='red', label='Izhikevic Model')
blue_patch = mpatches.Patch(color='blue', label='NEST Model')

plt.legend(handles=[red_patch,blue_patch])


plt.savefig(os.path.join(args.o,'test_bitwise_reproduction_mem.pdf'))

plt.close()

spk_plot(spk_izh_data,'r|')
spk_plot(spk_nest_data,'b.')

red_patch = mpatches.Patch(color='red', label='Izhikevic Model')
blue_patch = mpatches.Patch(color='blue', label='NEST Model')

plt.legend(handles=[red_patch,blue_patch])


plt.savefig(os.path.join(args.o,'test_bitwise_reproduction_spk.pdf'))
