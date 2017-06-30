import matplotlib
matplotlib.use('Agg')
import matplotlib.gridspec as gridspec
import pylab as plt
import helper as hf
import numpy as np
import matplotlib.mlab as mlab

def mem_spk_plot(data,times,sender,subplotspec):
    id=data[:,0]
    t=data[:,1]
    v=data[:,2]
    t_max=np.max(t)
    unique_sender=np.unique(id)
    gs1 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=subplotspec,  hspace=0.05)

    in_neurons=unique_sender[unique_sender>800]
    ex_neurons = unique_sender[unique_sender <= 800]
    if in_neurons.size>0 and ex_neurons.size>0:
        in_idx=in_neurons[0]
        ex_idx = ex_neurons[0]

        ax0 = plt.subplot(gs1[0, 0])
        ax1 = plt.subplot(gs1[1, 0])

        ax0.plot(t[id==in_idx],v[id==in_idx],'k',linewidth=0.2)
        ax0.plot(times[sender==in_idx-1],sender[sender==in_idx-1]*0,'b*',markersize=10)
        ax1.plot(t[id == ex_idx], v[id == ex_idx], 'k', linewidth=0.2)
        ax1.plot(times[sender == ex_idx-1], sender[sender == ex_idx-1] * 0, 'b*', markersize=10)
        for ax in [ax0,ax1]:
            ax.set_xlim([t_max-1000, t_max])
            ax.set_ylim([-100,100])
            ax.set_yticklabels([-50, 0, 50])
            ax.set_yticks([-50, 0, 50])
            xticks = np.linspace(0, 1000 , num=5,
                             endpoint=True)
        ax1.set_xticks(xticks+t_max-1000)

        ax1.set_xticklabels(xticks)


        ax0.set_xticks([])
        ax1.set_xlabel('Time [s]')


        ax1.set_ylabel('Membrane Potential [mv]')


def plot_raster_rate(times,senders,ax01,ax02,incolor='b',excolor='k'):
    exc_times, exc_sender,inh_times, inh_sender=hf.split_in_ex(times, senders)

    inh_rate, inh_bins = hf.bin_pop_rate(inh_times, inh_sender, 1.)
    exc_rate, exc_bins = hf.bin_pop_rate(exc_times, exc_sender, 1.)



    ax01.plot(exc_times, exc_sender, excolor,marker='.',linestyle='', markersize=1)
    ax01.plot(inh_times, inh_sender, incolor,marker='.',linestyle='', markersize=1)


    ax01.set_xlim([np.min(times), np.max(times)])
    ax01.set_ylim([0, 1000])
    ax01.set_xticks([])
    # ax01.set_xticklabels(np.linspace(0, 5, num=6,endpoint=True))
    # ax01.set_xlabel('Time [s]')
    ax01.set_ylabel('#Neuron')


    ax02.plot(inh_bins - np.min(times), inh_rate, incolor)
    ax02.plot(exc_bins - np.min(times), exc_rate, excolor)
    ax02.set_xlabel('Time [s]')
    ax02.set_ylabel('avg spk rate [spk/s]')
    ax02.set_xlim([np.min(times) - np.min(times), np.max(times) - np.min(times)])
    xticks=np.linspace(np.min(times) - np.min(times), np.max(times) - np.min(times)+2, num=5,
                                endpoint=True)
    ax02.set_xticks(xticks)
    ax02.set_xticklabels(xticks.astype(int)/1000)

    ax02.set_yticks([np.min(inh_rate),(np.min(inh_rate)+np.max(inh_rate))/2,np.max(inh_rate)])
def plot_weights(weights,ax,c='b',bins=40,normed=False,histtype='stepfilled',xlim=[0., 10.],ylim=[150., 50000],scale='log',linestyle='-',alpha=0.5):
    ax.hist(weights, bins=bins, normed=normed,histtype=histtype,color=c,linestyle=linestyle,alpha=alpha)
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    ax.set_xlabel('Synaptic weight [mV]')
    ax.set_ylabel('Frequency of Synaptic Weight')
    ax.set_yscale(scale)

def plot_psd(times,senders,ax,NFFT=512,noverlap=256,xlim=[0., 250.],ylim=[1e-3,1e2],scale='log',incolor='r',excolor='k'):
    exc_times, exc_sender,inh_times, inh_sender=hf.split_in_ex(times, senders)

    inh_rate, inh_bins = hf.bin_pop_rate(inh_times, inh_sender, 1.)
    exc_rate, exc_bins = hf.bin_pop_rate(exc_times, exc_sender, 1.)
    inh_Pxx, inh_freqs = mlab.psd(inh_rate-np.mean(inh_rate), NFFT=NFFT, Fs=1000. / (inh_bins[1] - inh_bins[0]),noverlap=noverlap)
    exc_Pxx, exc_freqs = mlab.psd(exc_rate-np.mean(exc_rate), NFFT=NFFT, Fs=1000. / (exc_bins[1] - exc_bins[0]),noverlap=noverlap)
    ax.plot(inh_freqs,inh_Pxx,incolor)
    ax.plot( exc_freqs,exc_Pxx, excolor)

    #ax3.plot(bins,freqs,Pxx)
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('Power [a.u.]')
    ax.set_yscale(scale)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_yticks([])


def plot_specgram(times,senders,t_min,t_max,weights,outname):
    idx=(times>t_min)&(times<=t_max)

    exc_sender = senders[senders <= 800]
    exc_times = times[senders <= 800]
    inh_sender = senders[senders > 800]
    inh_times = times[senders > 800]
    inh_rate, inh_bins = hf.bin_pop_rate(inh_times, inh_sender, 1.)
    exc_rate, exc_bins = hf.bin_pop_rate(exc_times, exc_sender, 1.)

    fig = plt.figure(figsize=(9, 8))
    gs0 = gridspec.GridSpec(2, 2)
    gs0.update(left=0.1, right=0.97, top=0.97, bottom=0.06, hspace=0.15)

    gs1 = gridspec.GridSpecFromSubplotSpec(5, 1, subplot_spec=gs0[0,:])

    ax2 = plt.subplot(gs0[1,0])
    ax3 = plt.subplot(gs0[1,1])

    ax01 = plt.subplot(gs1[:4,0])
    ax02 = plt.subplot(gs1[4, 0])

    ax01.plot(times[idx],senders[idx],'k.',markersize=2)
    ax01.set_xlim([np.min(times[idx]),np.max(times[idx])])
    ax01.set_ylim([0, 1000])
    ax01.set_xticks([])
    #ax01.set_xticklabels(np.linspace(0, 5, num=6,endpoint=True))
    #ax01.set_xlabel('Time [s]')
    ax01.set_ylabel('#Neuron')
    ax01.set_title('sec = {}, ex rate {} and cv {},  in rate {} and cv {} '.format(
        int(np.min(times)/1000),
        np.around(np.mean(exc_rate),1),
        np.around(np.std(exc_rate)/np.mean(exc_rate),1),
        np.around(np.mean(inh_rate), 1),
        np.around(np.std(inh_rate) / np.mean(inh_rate), 1)),
        loc='left')

    ax02.plot(inh_bins-np.min(times[idx]), inh_rate, 'r')
    ax02.plot(exc_bins-np.min(times[idx]), exc_rate, 'k')
    ax02.set_xlim([np.min(times[idx])-np.min(times[idx]),np.max(times[idx])-np.min(times[idx])])
    ax02.set_xticks(np.linspace(np.min(times[idx])-np.min(times[idx]),np.max(times[idx])-np.min(times[idx]), num=6, endpoint=True))

    ax02.set_xlabel('Time [s]')
    ax02.set_ylabel('avg spk rate [spk/s]')



    ax3.psd(inh_rate-np.mean(inh_rate), NFFT=512, Fs=1000. / (inh_bins[1]-inh_bins[0]),noverlap=256)
    ax3.psd(exc_rate-np.mean(exc_rate), NFFT=512, Fs=1000. / (exc_bins[1] - exc_bins[0]))

    #ax3.plot(bins,freqs,Pxx)
    ax3.set_xlabel('Frequency [Hz]')
    ax3.set_ylabel('Power [a.u.]')
    ax3.set_xlim([0,200.])
    plt.savefig(outname)
    plt.close()


def plot_group(group, ax, LP=False, numbers=True):
    N_fired = group['N_fired']
    times, senders = hf.get_t_s(group)
    idx_in = senders > 800
    idx_ex = senders < 800
    ax1 = ax.twinx()

    ax.scatter(times[idx_ex], senders[idx_ex], s=80, facecolors='none', edgecolors='r')
    ax1.scatter(times[idx_in], (senders[idx_in] - 800) * 4, s=80, facecolors='k')

    for link in group['links']:
        if link['post'] < 799:
            post_i = link['post']
        else:
            post_i = (link['post'] - 800) * 4
        pre_times = times[link['pre'] == senders]
        if pre_times.size > 1:
            pre_times = [pre_times[0]]
        post_times = times[link['post'] == senders]
        if post_times.size > 1:
            post_times = [post_times[0]]

        ax.plot([pre_times, post_times],
                [link['pre'], post_i], 'k')
        if numbers:
            ax.text(times[link['pre'] == senders] + 1,
                    link['pre'] - 10,
                    s=str(link['pre']),
                    fontsize=12)

            ax.text(times[link['post'] == senders] + 1,
                    post_i - 10,
                    s=str(link['post']),
                    fontsize=12)

    if LP:

        i = len(group['links']) - 1
        while group['links'][i]['layer'] >= 2:
            i_l = i
            if group['links'][i]['post'] < 799:
                post_i = group['links'][i]['post']
            else:
                post_i = (group['links'][i]['post'] - 800) * 4
            ax.plot([times[group['links'][i]['pre'] == senders],
                     times[group['links'][i]['post'] == senders]], [group['links'][i]['pre'],
                                                                    post_i], 'k', linewidth=4, alpha=0.5)
            if group['links'][i]['layer'] == group['L_max']:
                ax.text(times[group['links'][i]['post'] == senders] - 20,
                        post_i + 20,
                        s='longest path',
                        fontsize=11)
            for j in range(len(group['links'])):
                if group['links'][j]['post'] == group['links'][i]['pre']:
                    i_l = j
            if group['links'][i]['layer'] == 2:
                break
            i = i_l

    ax.set_ylim(-20, 820)
    ax1.set_ylim(-20, 820)

    ax.set_yticks([0, 400, 800])

    ax1.set_yticks([0, 800])
    ax1.set_yticklabels([800, 1000])

    ax.set_xlim(np.min(times) - 10, np.max(times) + 10)
    ax1.set_xlim(np.min(times) - 10, np.max(times) + 10)


def plot_8(group_data, outname):
    fig = plt.figure("plot 8")
    ax0 = fig.add_subplot(221)
    ax1 = fig.add_subplot(222)
    ax2 = fig.add_subplot(223)
    ax3 = fig.add_subplot(224)

    N_list = []
    L_list = []
    T_list = []
    for i, g in enumerate(group_data):
        times, senders = hf.get_t_s(g)

        N_list.append(int(g["N_fired"]))

        T_list.append(max(times))  # time span

        L_list.append(int(g["L_max"]))  # longest path

    ax1.hist(N_list, 100)
    ax1.set_title('# of neurons, total {}'.format(len(group_data)))
    ax2.hist(T_list, 100)
    ax2.set_title('time span[ms]')
    ax3.hist(L_list, 30)
    ax3.set_title('length of longest path')

    if len(group_data) > 1:
        plot_group(g, ax0, LP=True, numbers=False)

    plt.savefig(outname)


def plot_5(times, senders, outname):
    fig = plt.figure(figsize=(9, 12))
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    tmin = np.min(times)

    for t, ax in [(0, ax1), (100, ax2), (3600, ax3)]:
        idx = (times > (t * 1000 + tmin)) & (times < (t * 1000 + 1000. + tmin))
        sub_times = times[idx]
        sub_senders = senders[idx]
        ax.plot(sub_times, sub_senders, 'k.')
        ax.set_xticks(np.min(times) + np.linspace(0, 1000, 6, endpoint=True))
        ax.set_xticklabels(np.linspace(0, 1000, 6, endpoint=True).astype(int))
        ax.set_xlim([np.min(times), np.min(times) + 1000])
        ax.set_ylabel('#Neuron')
        ax.set_title('sec = {}'.format(int(t)), loc='left')
    ax3.set_xlabel('Time[ms]')
    plt.savefig(outname)
    plt.close()

