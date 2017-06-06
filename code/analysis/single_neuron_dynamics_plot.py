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

def mem_plot(data,spk,c):
    id=data[:,0]
    t=data[:,1]
    v=data[:,2]
    u = data[:, 3]
    I = data[:, 4]

    sender=spk[:,0]
    times=spk[:,1]
    t_max=np.max(t)
    for i,idx in enumerate(np.unique(id[id>800])):

        plt.subplot(2, 2,i+1)
        plt.plot(t[id==idx],v[id==idx],c,linewidth=0.2)
        plt.plot(t[id==idx],u[id==idx],c,linewidth=0.2)
        plt.plot(t[id == idx], I[id == idx], c, linewidth=0.2)

        plt.plot(times[sender==idx],sender[sender==idx]*0,c+'*',markersize=10)

        plt.xlim([t_max-1100., t_max-1000])
        plt.ylim([-100,100])
        if i>=3:
            break



def spk_plot(data,c):
    id=data[:,0]
    t=data[:,1]
    idx=t>36000
    t_max=np.max(t)

    plt.plot(t[idx],id[idx],c)
    plt.plot(t[idx], id[idx], c)

    plt.xlim([t_max - 1100., t_max-000])


spk_izh_data=np.loadtxt(args.si)
spk_izh_data[:,0]=spk_izh_data[:,0]+1
spk_nest_data=np.loadtxt(args.sn)

data_len=len(spk_izh_data)
spk_izh_data=spk_izh_data[:data_len]
spk_nest_data=spk_nest_data[:data_len]


difference=spk_izh_data[:data_len]-spk_nest_data[:data_len]
idx=np.where(difference>=0.001)[0]



izh_data=np.loadtxt(args.i)
izh_data=izh_data[1000:]
nest_data=np.loadtxt(args.n)

idx_izh=izh_data[:,0]
t_izh=izh_data[:,1]
v_izh=izh_data[:,2]
u_izh=izh_data[:,3]
I_izh=izh_data[:,4]
t_nest=nest_data[:,1]
v_nest=nest_data[:,2]
u_nest=nest_data[:,3]
I_nest=nest_data[:,4]





difference=izh_data-nest_data
idx=np.where(np.abs(difference)>=0.0001)[0]

print izh_data[idx,1]
print np.unique(izh_data[idx[50:],0])
print nest_data[idx,0]
print izh_data[idx] - nest_data[idx]

mem_plot(izh_data,spk_izh_data,'r')
mem_plot(nest_data,spk_nest_data,'b')


# red_patch = mpatches.Patch(color='red', label='Izhikevic Model')
# blue_patch = mpatches.Patch(color='blue', label='NEST Model')

#plt.legend(handles=[red_patch,blue_patch])


plt.savefig(os.path.join(args.o,'membrane_potential_comparison.pdf'))

plt.close()

spk_plot(spk_izh_data,'r|')
spk_plot(spk_nest_data,'b.')

red_patch = mpatches.Patch(color='red', label='Izhikevic Model')
blue_patch = mpatches.Patch(color='blue', label='NEST Model')

plt.legend(handles=[red_patch,blue_patch])


plt.savefig(os.path.join(args.o,'spikes_comparison.pdf'))
