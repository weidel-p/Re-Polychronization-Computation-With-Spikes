import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from helper import *
import os
import matplotlib.gridspec as gridspec
# SMALL_SIZE = 8
# MEDIUM_SIZE = 10
# BIGGER_SIZE = 12
#
# plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
# plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
# plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
# plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def plot_7(line,ax,LP=False,numbers=False):
    N_fired= count_neurons(line)
    lengh= length(line)
    times, senders= fire_times(line)
    pre,post, delay, layer= links(line)
    idx_in=senders>800
    idx_ex = senders < 800
    ax1 = ax.twinx()

    ax.scatter(times[idx_ex], senders[idx_ex], s=80, facecolors='none', edgecolors='r')
    ax1.scatter(times[idx_in], (senders[idx_in]-800)*4,   s=80, facecolors='k')


    for i in range(len(pre)):
        if post[i]<799:
            post_i=post[i]
        else:
            post_i =(post[i]-800)*4

        ax.plot( [times[pre[i]==senders],times[ post[i]==senders]],
                  [pre[i],post_i],'k')
        if numbers:

            ax.text(times[pre[i]==senders]+1,
                     pre[i]-10,
                     s=str(pre[i]),
                     fontsize=12)

            ax.text(times[ post[i]==senders]+1,
                    post_i-10,
                     s=str(post[i]),
                     fontsize=12)

    if LP:

        i= layer.index(max(layer))

        while layer[i] >1:
            if post[i] < 799:
                post_i = post[i]
            else:
                post_i = (post[i] - 800) * 4
            ax.plot([times[ pre[i]==senders],
                     times[post[i] == senders]], [pre[i],
                                                  post_i], 'k', linewidth=4)
            if layer[i] == max(layer):
                ax.text(times[ post[i]==senders]- 20,
                        post_i + 20,
                         s='longest path',
                         fontsize=11)
            i = post.index(pre[i])
        if post[i] < 799:
            post_i = post[i]
        else:
            post_i = (post[i] - 800) * 4
        ax.plot([times[ pre[i]==senders],
                 times[post[i] == senders]], [pre[i],
                                              post_i], 'k', linewidth=4)
    ax.set_ylim(-20,820)
    ax1.set_ylim(-20,820)

    ax.set_yticks([0, 400,800])

    ax1.set_yticks([0,800])
    ax1.set_yticklabels([800, 1000])

    ax.set_xlim(np.min(times)-10,np.max(times)+10)
    ax1.set_xlim(np.min(times)-10,np.max(times)+10)

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
    ax2.hist(T_list,20)
    ax2.set_title('time span[ms]')
    ax3.hist(L_list, 20)
    ax3.set_title('length of longest path')


def plot_6(folder,timestep,matching=0.4):

    spikes = np.loadtxt(os.path.join(folder,'spikes-{}-0.gdf'.format(timestep+1003)))

    senders=spikes[:,0]
    times =spikes[:,1]
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
                    found,count= match_pattern(sub_times,sub_senders,t,group,matching)
                    if found:
                        gr_senders =np.in1d(sub_senders,group['senders'])
                        sub_sub_senders=sub_senders[gr_senders]
                        sub_sub_times = sub_times[gr_senders]

                        plt.plot(group['times']+t,group['senders'],'ro')
                        plt.plot(sub_sub_times,sub_sub_senders,'bx')
                        #plt.plot(sub_times,sub_senders,'bo',mfc='none')

                        #plt.xlim(t-2.0,t+group['times'][-1]+5.0)
                        plt.title('{},{}'.format(t,s))

                        plt.savefig('../../figures/{}_{}_{}.png'.format(timestep,n,t))
                        plt.close()
                    else:
                        if maximum< count and count > 0.1:
                            maximum= count


def plot_5(folder,t1,t2,t3):
    fig = plt.figure(figsize=(9, 12))
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    for t,ax in [(t1,ax1),(t2,ax2),(t3,ax3)]:
        spikes = np.loadtxt(os.path.join(folder,'spikes-{}-0.gdf'.format(t+1002)))
        senders = spikes[:, 0]
        times = spikes[:, 1]
        idx=(times>(np.min(times))) & (times<(np.min(times)+1000.))
        sub_times=times[idx]
        sub_senders=senders[idx]
        ax.plot(sub_times,sub_senders,'k.')
        ax.set_xticks(np.min(times)+np.linspace(0,1000,6,endpoint=True))
        ax.set_xticklabels(np.linspace(0, 1000, 6, endpoint=True).astype(int))
        ax.set_xlim([np.min(times),np.min(times)+1000])
        ax.set_ylabel('#Neuron')
        ax.set_title('sec = {}'.format(int(np.min(times)/1000.)),loc='left')
    ax3.set_xlabel('Time[ms]')
    plt.savefig('../../figures/plot_5.png')
    plt.close()

def plot_specgram(folder,timestep):
    spikes = np.loadtxt(os.path.join(folder, 'spikes-{}-0.gdf'.format(timestep + 1002)))
    senders = spikes[:, 0]
    times = spikes[:, 1]
    exc_sender = senders[senders < 800]
    exc_times = times[senders < 800]
    inh_sender = senders[senders > 800]
    inh_times = times[senders > 800]
    inh_rate, inh_bins = bin_pop_rate(inh_times, inh_sender, 5.)
    exc_rate, exc_bins = bin_pop_rate(exc_times, exc_sender, 5.)
    freqs, Pxx, bins=calc_specgram(exc_bins, exc_rate-np.mean(exc_rate), NFFT=1024, noverlap=900)

    weights = np.loadtxt(os.path.join(folder, 'weights_{:02d}.dat'.format(timestep )))
    weights=weights[:,2]
    fig = plt.figure(figsize=(9, 8))
    gs2 = gridspec.GridSpec(2, 2)
    gs2.update(left=0.1, right=0.97, top=0.97, bottom=0.06, hspace=0.15)

    ax0 = plt.subplot(gs2[0,0])
    ax1 = plt.subplot(gs2[0,1])
    ax2 = plt.subplot(gs2[1,0])
    ax3 = plt.subplot(gs2[1,1])


    idx = (times > (np.min(times))) & ((times < (np.min(times)+5000.) ))
    ax0.plot(times[idx],senders[idx],'k.',markersize=2)
    ax0.set_xlim([np.min(times),np.min(times)+5000])
    ax0.set_ylim([0, 1000])
    ax0.set_xticks(np.linspace(np.min(times),np.min(times)+5000, num=6, endpoint=True))
    ax0.set_xticklabels(np.linspace(0, 5, num=6,endpoint=True))
    ax0.set_xlabel('Time [s]')
    ax0.set_ylabel('#Neuron')
    ax0.set_title('sec = {}'.format(int(np.min(times)/1000)), loc='left')

    ax1.plot(inh_bins, inh_rate, 'r')
    ax1.plot(exc_bins, exc_rate, 'k')
    ax1.set_xlim([np.min(inh_bins),np.max(inh_bins)])
    ax1.set_xticks(np.linspace(np.min(inh_bins), np.max(inh_bins),3,endpoint=True))
    ax1.set_xticklabels(np.linspace(np.min(inh_bins), np.max(inh_bins), 3, endpoint=True).astype(int)/1000)

    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Population averaged firing rate [spk/s]')

    ax2.hist(weights, bins=20, normed=True)
    ax2.set_ylim([0., 1.4])
    ax2.set_xlim([0.,10.])
    ax2.set_xlabel('Synaptic weight [mV]')
    ax2.set_ylabel('normed count')

    ax3.pcolormesh(bins,freqs,Pxx)
    ax3.set_ylabel('Frequency [Hz]')
    ax3.set_xlabel('Time [s]')
    plt.savefig('../../figures/{}th_timestep.png'.format(timestep))
    plt.close()

def weight_convergence(folder):
    weight_stack=np.zeros((N_measure,20))

    for timestep in range(N_measure):

        weights = np.loadtxt(os.path.join(folder, 'weights_{:02d}.dat'.format(timestep)))
        weights = weights[:, 2]
        weight_hist, bin_edges = np.histogram(weights, np.linspace(0, 10,num=21,endpoint=True),normed=True)
        weight_stack[timestep,:]=weight_hist
        plt.plot(bin_edges[:-1]+0.5*(bin_edges[1]-bin_edges[0]),weight_hist)

    plt.savefig('../../figures/weight_stack.png')
    plt.close()
    c=np.corrcoef(weight_stack)
    plt.subplot(211)
    plt.imshow(c)

    plt.subplot(212)
    plt.plot(c[-1,:])
    plt.savefig('../../figures/weight_corr.png')
    plt.close()



weight_convergence('../../data')

for timestep in range(N_measure):
    plot_specgram('../../data', timestep)

for timestep in range(N_measure):
    plot_6('../../data/', timestep, 0.4)

plot_5('../../data/', 0, 1, 36)




f=open('../../data/target_{:02d}.txt'.format(timestep))
graph=f.readlines()
fig = plt.figure()
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
        plot_7(line,ax0,LP=True,numbers=False)
        break
plt.savefig('../../figures/plot_8.png')
plt.close()


j=0
for i,line in enumerate(graph):
    N=count_neurons(line)
    times, senders= fire_times(line)
    cond=(N<20) & (len(senders)==np.unique(senders).size)

    if cond:
        fname='../../figures/{}_plot_7_{:04d}.png'.format(timestep,i)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plot_7(line,ax,LP=False,numbers=True)
        plt.savefig(fname)
        plt.close()
        j+=1
    if j>10:
        break
fig = plt.figure()
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
plt.savefig('../../figures/plot_8.png')
plt.close()




