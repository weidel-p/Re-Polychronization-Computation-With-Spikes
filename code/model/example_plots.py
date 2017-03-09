import matplotlib.pyplot as plt
import numpy as np
from helper import *
import os

def plot_7(line,ax,LP=False):
    N_fired= count_neurons(line)
    lengh= length(line)
    times, senders= fire_times(line)
    pre,post, delay, layer= links(line)
    if len(senders)==np.unique(senders).size:

        ax.plot(times, senders,'ro')
        ax.set_ylim(0,1000)
        for i in range(len(pre)):
            if post[i]<799:
                ax.plot( [times[senders.index(pre[i])],times[ senders.index(post[i])]],
                          [pre[i],post[i]],'b')

                ax.text(times[ senders.index(pre[i])]+1,
                         pre[i]-10,
                         s=str(pre[i]),
                         fontsize=12)

                ax.text(times[ senders.index(post[i])]+1,
                         post[i]-10,
                         s=str(post[i]),
                         fontsize=12)
            else:
                ax.plot( [times[senders.index(pre[i])],
                           times[senders.index(post[i])]],
                          [pre[i],
                           post[i]],'r')
        if LP:
            i= layer.index(max(layer))
            while layer[i] >1:
                ax.plot([times[senders.index(pre[i])],
                          times[senders.index(post[i])]], [pre[i],
                                                           post[i]], 'b', linewidth=4)
                if layer[i] == max(layer):
                    ax.text(times[senders.index(post[i])] - 20,
                             post[i] + 20,
                             s='longest path',
                             fontsize=11)
                i = post.index(pre[i])
            ax.plot([times[senders.index(pre[i])],
                      times[senders.index(post[i])]], [pre[i],
                                                       post[i]], 'b', linewidth=4)


def plot_8( graph,ax1,ax2,ax3):
    N_list=[]
    L_list=[]
    T_list=[]
    for i,line in enumerate(graph):
            N_fired=count_neurons(line)
            N_list.append(N_fired)
            times,senders= fire_times(line)
            pre, post, delay, layer= links(line)
            lengh= max(layer)
            L_list.append(lengh)
            T_list.append(max(times))
    ax1.hist(N_list,20)
    ax1.set_title('# of neurons')
    ax2.hist(L_list,20)
    ax2.set_title('length of longest path')
    ax3.hist(T_list,20)
    ax3.set_title('time span[ms]')


def plot_6(folder,timestep):

    spikes_before = np.loadtxt(os.path.join(folder,'spikes-{}-0.gdf'.format(timestep+1002)))
    spikes_after  = np.loadtxt(os.path.join(folder, 'spikes-{}-0.gdf'.format(timestep + 1 + 1002)))
    t_max=np.max(spikes_before[:,1])
    spikes=np.append(spikes_before,spikes_after,axis=0)
    senders=spikes[:,0]
    times =spikes[:,1]
    idx=np.abs(times-t_max)<100000.
    senders=senders[idx]
    times = times[idx]
    group_container=[]
    graphname=os.path.join(folder, 'target_{:02d}.txt'.format(timestep))
    graph=open( graphname)

    for line in graph:
        N,L,time,sender, pre,post ,delay, layer= strip_graph(line )
        if N<25 and (len(sender)==np.unique(sender).size):
            group_container.append({'N':N,'L':L,'senders':sender, 'times':time,'pre':pre, 'post' : post, 'delay':delay ,'layer' : layer})


    maximum=0
    from tqdm import tqdm

    for n,group in tqdm(enumerate(group_container)):

        for s,t in zip(senders,times):
            if ((int(s ) in group[ 'senders']) and (int(s) in group['pre'])):
                if group['layer'][group['pre'].index(int(s))] ==1:
                    idx_t = (times > t - 5.) & (times < t+np.max(group['times']) + 5.0)
                    sub_times=times[idx_t]
                    sub_senders=senders[idx_t]
                    found,count= match_pattern(sub_times,sub_senders,t,group,0.4)
                    if found:
                        gr_senders =np.in1d(sub_senders,group['senders'])
                        sub_sub_senders=sub_senders[gr_senders]
                        sub_sub_times = sub_times[gr_senders]

                        print( '{}, {} \n {}'. format (t,s,group,count))
                        plt.plot(group['times']+t,group['senders'],'ro')
                        plt.plot(sub_sub_times,sub_sub_senders,'bx')
                        #plt.plot(sub_times,sub_senders,'bo',mfc='none')

                        #plt.xlim(t-2.0,t+group['times'][-1]+5.0)
                        plt.title('{},{}'.format(t,s))

                        plt.savefig('{}_{}.png'.format(n,t))
                        plt.close()
                    else:
                        if maximum< count and count > 0.1:
                            maximum= count
                            print(t,s,count,group['N'])


def plot_5(folder,timestep):
    spikes = np.loadtxt(os.path.join(folder,'spikes-{}-0.gdf'.format(timestep+1002)))
    sender = spikes[:, 0]
    times = spikes[:, 1]
    exc_sender = times[senders<800]
    exc_times = senders[senders<800]
    inh_sender = times[senders > 800]
    inh_times = senders[senders > 800]

    inh_rate,inh_bins=bin_pop_rate(inh_times,inh_sender)
    exc_rate, exc_bins = bin_pop_rate(exc_times, exc_sender)
    plt.plot(inh_bins,inh_rate,'r')
    plt.plot(exc_bins,exc_rate,'k')
    plt.savefig('{}_rate'.format(timestep))
    path=os.listdir('../data')

    idx=times<(np.min(times)+1000.)
    plt.plot(times[idx],senders[idx],'b.')

    plt.savefig('../figures/raster_{}.png'.format(timestep))
    plt.close()


timestep=2
plot_5('../analysis/',timestep)

plot_6('../analysis/',timestep)

f=open('../analysis/target_{:02d}.txt'.format(timestep))
graph=f.readlines()
for i,line in enumerate(graph):
    N=count_neurons(line)
    times, senders= fire_times(line)
    cond=(N<30) & (len(senders)==np.unique(senders).size)

    if cond:
        fname='plot_7_{:04d}.png'.format(i)
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111)
        plot_7(line,ax,False)
        plt.savefig(fname)
        plt.close()

fig = plt.figure(figsize=(12, 9))
ax0 = fig.add_subplot(221)
ax1 = fig.add_subplot(222)
ax2 = fig.add_subplot(223)
ax3 = fig.add_subplot(224)
plot_8(graph,ax1,ax2,ax3)

for i,line in enumerate(graph):
    N=count_neurons(line)
    times, senders= fire_times(line)
    cond=(N<20) & (len(senders)==np.unique(senders).size)
    if cond:
        plot_7(line,ax0,LP=True)
        break
plt.savefig('plot_8.png')
plt.close()




