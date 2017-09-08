import argparse
import numpy as np
import os,sys
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import mpl_toolkits.axes_grid.inset_locator
import helper as hf
import plot_helper as phf
import seaborn as sns
import scipy.stats as stat
matplotlib.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
font = {'family':'serif','size':18}
plt.rc('font',**font)
plt.rc('legend',**{'fontsize':16})
flatui = [ sns.xkcd_rgb["dusty purple"],sns.xkcd_rgb["faded green"]]
plt.figure()
current_palette = sns.color_palette(flatui)
sns.palplot(current_palette)
sns.set_palette(current_palette)
plt.savefig('palette.png')
plt.close()

#sns.set_palette(sns.light_palette("blue"))
parser = argparse.ArgumentParser()
parser.add_argument("-sl", '--spikelist', help="list of spike files", nargs="+")
parser.add_argument("-gl", '--grouplist',help="list of group files", nargs="+")
parser.add_argument("-cl", '--connectivitylist', help="list of connectivity files", nargs="+")

parser.add_argument('--gamma_plot', type=str)
parser.add_argument('--group_plot', type=str)

args = parser.parse_args()
fig=plt.figure(figsize=(15,6))


gs0 = gridspec.GridSpec(1, 3)
gs0.update(left=0.05, right=0.95, top=0.95, bottom=0.15, hspace=0.2,wspace=0.25)

ax = plt.subplot(gs0[0, 0])

ax_low = plt.subplot(gs0[0, 2])
ax_high = plt.subplot(gs0[0, 1])
low_gamma=0
high_gamma=0
N_high = []
L_high = []
T_high = []
N_low = []
L_low = []
T_low = []
N_groups_high=[]
N_groups_low=[]
for i,connectivity,spikes,groupfile in zip(range(len(args.spikelist)),args.connectivitylist,args.spikelist,args.grouplist):
    connectivity = hf.load_json(connectivity)
    all_w, ex_ex_w, ex_in_w = hf.conn_dist(connectivity, 'weight')
    all_d, ex_ex_d, ex_in_d = hf.conn_dist(connectivity, 'delay')
    weights,delays,counts=hf.weight_delay_histograms(np.append(ex_ex_w,ex_in_w), np.append(ex_ex_d,ex_in_d))
    max_idx=np.argmax(counts)
    idx=np.unravel_index(max_idx, counts.shape)
    delay_of_max=delays[idx[0],idx[1]]
    color = 'C0'
    try:
        if delay_of_max>16:
            color='C1'
            if low_gamma==0:
                cmap = sns.light_palette("C1", as_cmap=True)

                phf.plot_2D_weights(weights, delays, counts, ax_low,cmap=cmap)
            N_list, T_list, L_list = phf.return_NTL(groupfile)
            N_low += N_list
            T_low += T_list
            L_low += L_list
            N_groups_low.append(len(N_list))
            low_gamma+=1


        if delay_of_max < 16:
            color='C0'
            if high_gamma==0:
                cmap = sns.light_palette("C0", as_cmap=True)

                phf.plot_2D_weights(weights, delays, counts, ax_high,cmap=cmap)

            high_gamma += 1
            N_list, T_list, L_list = phf.return_NTL(groupfile)
            N_high+=N_list
            T_high+=T_list
            L_high+=L_list
            N_groups_high.append(len(N_list))
    except:
        continue
    times, senders = hf.read_spikefile(spikes)
    phf.plot_psd(times, senders, ax=ax,incolor=None,excolor=color)
    del times,senders,weights,delays,connectivity,all_d, ex_ex_d, ex_in_d,all_w, ex_ex_w, ex_in_w,N_list,L_list,T_list
    print('gamma plot {}'.format(i))





axin1 = mpl_toolkits.axes_grid.inset_locator.inset_axes(ax,
                                                        width="45%",  # width = 30% of parent_bbox
                                                        height=1.5,  # height : 1 inch
                                                        borderpad=1.5
                                                        )



labels =  'low gamma','high gamma',
fracs = [low_gamma,high_gamma]
explode=( 0.1, 0)

plt.pie(fracs, explode=explode, labels=labels,colors=[r'C1',r'C0'],
                autopct='%1.1f%%', shadow=True, startangle=-95)

plt.savefig(args.gamma_plot)
plt.close()

group_dict=dict(N=N_high+N_low,
                L=L_high+L_low,
                T=T_high+T_low,
                gamma=len(N_high)*['high']+len(N_low)*['low']
                )

N_group_dict = dict(N_groups=N_groups_high + N_groups_low,

                  gamma=len(N_groups_high) * ['high'] + len(N_groups_low) * ['low']
                  )
KS_N_groups = stat.ks_2samp(N_groups_high, N_groups_low)
KS_N = stat.ks_2samp(N_high, N_low)
KS_L = stat.ks_2samp(L_high, L_low)
KS_T = stat.ks_2samp(T_high, T_low)
del N_high,N_low,L_high,L_low,T_high,T_low
import pandas as pd
data=pd.DataFrame(group_dict)
N_data=pd.DataFrame(N_group_dict)




fig=plt.figure(figsize=(20,6))


gs0 = gridspec.GridSpec(1, 4)
gs0.update(left=0.05, right=0.97, top=0.93, bottom=0.1, hspace=0.15)

ax_N_groups = plt.subplot(gs0[0, 0])

ax_N = plt.subplot(gs0[0, 1])
ax_L = plt.subplot(gs0[0, 2])
ax_T = plt.subplot(gs0[0, 3])

print('violin')
ax_N_groups = sns.boxplot(x="gamma", y="N_groups", data=N_data, ax=ax_N_groups,showfliers=False)
print('swarm')

ax_N_groups = sns.swarmplot(x="gamma", y="N_groups", data=N_data,
                color="black", edgecolor="gray",ax=ax_N_groups)
ax_N_groups.set_ylabel('Number of groups found')
ax_N_groups.set_xlabel('Spectral peak')

#plt.suptitle('Number of groups: high gamma {0:5.1f}+-{1:5.1f} low gamma {2:5.1f}+-{3:5.1f}'.format(np.mean(N_groups_high),np.std(N_groups_high),np.mean(N_groups_low),np.std(N_groups_low)))
print('1.')
ax_N = sns.boxplot(x='gamma',y='N',data=data,ax=ax_N,showfliers=False
                   )
ax_N.set_ylabel('Groupsize')
ax_N.set_ylim([0,200])
ax_N.set_xlabel('Spectral peak')

print('2.')

ax_L = sns.boxplot(x='gamma', y='L', data=data,ax=ax_L,showfliers=False
                )
ax_L.set_ylabel('Longest path')
ax_L.set_ylim([0,15])
ax_L.set_xlabel('Spectral peak')


print('3.')

ax_T = sns.boxplot(x='gamma', y='T', data=data,ax=ax_T,showfliers=False
                )
ax_T.set_ylabel('Timespan')
ax_T.set_xlabel('Spectral peak')
ax_T.set_ylim([0,200])





# ax_N_groups.set_title('KS statistic = {0:4.3f}, p-value = {1:4.3f}'.format(KS_N_groups.statistic,KS_N_groups.pvalue))
# ax_N.set_title('KS statistic = {0:4.3f}, p-value = {1:4.3f}'.format(KS_N.statistic,KS_N.pvalue))
# ax_L.set_title('KS statistic = {0:4.3f}, p-value = {1:4.3f}'.format(KS_L.statistic,KS_L.pvalue))
# ax_T.set_title('KS statistic = {0:4.3f}, p-value = {1:4.3f}'.format(KS_T.statistic,KS_T.pvalue))


plt.savefig(args.group_plot)


