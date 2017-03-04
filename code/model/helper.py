import numpy as np
import nest
import matplotlib.pyplot as plt
from params import *

import time
colors=['b','g','r','purple','black','y','cyan','r','r','r','r','r','r','r']

def count_neurons(line):
	line=line.split(',')
	return int(line[0].split()[2])
def length(line):
	line=line.split(',')
	return int(line[1].split()[2])
def fire_times(line):
	senders=[]
	times=[]
	line=line.split(',')
	N_fired=int(line[0].split()[2])
	for i in range(N_fired):
		senders.append(int(line[2+2*i].split()[2])-1)
		times.append(int(line[3+2*i].split()[2]))
	return times,senders
def links(line):
	N_fired=int(line.split(',')[0].split()[2])
	linecount=N_fired*2+2
	line=line.split('links')
	line=line[1:]
	pre,post,delay,layer=[],[],[],[]
	for i in line:
		container=(i.split())
		pre.append(int(container[2][1:-1]))
		post.append(int(container[3][:-1]))
		delay.append(int(container[4][:-1]))
		layer.append(int(container[5][:-2]))
	return pre,post,delay,layer


def plot_7(line):
	N_fired=count_neurons(line)
	lengh=length(line)
	times,senders=fire_times(line)
	pre,post,delay,layer=links(line)
	plt.plot(times,senders,'ro')
	plt.ylim(0,1000)
	for i in range(len(pre)):
		if post[i]<799:
			plt.plot( [times[senders.index(pre[i])],
			times[senders.index(post[i])]],[pre[i],
			post[i]],'b')

			plt.text(times[senders.index(pre[i])]+1,
			pre[i]-10,
			s=str(pre[i]),
			fontsize=12)

			plt.text(times[senders.index(post[i])]+1,
			post[i]-10,
			s=str(post[i]),
			fontsize=12)
		else: 
			plt.plot( [times[senders.index(pre[i])],
			times[senders.index(post[i])]],
			[pre[i],
			post[i]],'r')

def plot_8(graph):
	N_list=[]
	L_list=[]
	T_list=[]
	for i,line in enumerate(graph):
		if False:
			N_fired=count_neurons(line)
			N_list.append(N_fired)
			lengh=length(line)
			L_list.append(lengh)
			times,senders=fire_times(line)
			pre,post,delay,layer=links(line)
			plt.subplot(2,2,1)
			plt.title('time span')
			plt.plot(times,senders,'ro')
			
			i=layer.index(max(layer))
			T_list.append(max(times))
			while layer[i]>2:
				plt.plot( [times[senders.index(pre[i])],
						times[senders.index(post[i])]],[pre[i],
						post[i]],'b',linewidth=4)
				plt.text(times[senders.index(post[i])]+1,
					post[i]+50,
					s=str(post[i]),
					fontsize=12)
				if layer[i]==max(layer):
					plt.text(times[senders.index(post[i])]-20,
						post[i]+20,
						s='longest path',
						fontsize=11)
				i=post.index(pre[i])
			plt.plot( [times[senders.index(pre[i])],
				times[senders.index(post[i])]],[pre[i],
				post[i]],'b',linewidth=4)
			plt.text(times[senders.index(post[i])]+1,
				post[i]+50,
				s=str(post[i]),
				fontsize=12)
			plt.text(times[senders.index(pre[i])]+1,
				pre[i]+50,
				s=str(pre[i]),
				fontsize=12)
			plt.ylim(0,1000)
			
			for i in range(len(pre)):
					plt.plot( [times[senders.index(pre[i])],
					times[senders.index(post[i])]],[pre[i],
					post[i]],'black')
		else:
			times,senders=fire_times(line)
			lengh=length(line)
			N_fired=count_neurons(line)
			N_list.append(N_fired)
			L_list.append(lengh)
			T_list.append(max(times))
			print(i)
	graph.close()
	plt.subplot(2,2,2)
	plt.hist(N_list,20)
	plt.title('# of neurons')
	plt.subplot(2,2,4)
	plt.hist(L_list,20)
	plt.title('length of longest path')
	plt.subplot(2,2,3)
	T_list.pop(T_list.index(max(T_list)))
	plt.hist(T_list,20)
	plt.title('time span[ms]')


def plot_6(timestep):
	if timestep <8:
		
		spikes=np.loadtxt('spike-10{}-0.gdf'.format('0{}'.format(timestep+2)))
	else:
		spikes=np.loadtxt('spike-10{}-0.gdf'.format(timestep+2))
	print(len(spikes))	
	#load all polygroups
	group_container=[]
	graphname='try_graph_{}.dat'.format(timestep)
	graph=open(graphname)

	for line in graph:
		N,L,time,sender,pre,post,delay,layer=strip_graph(line)
		if N<20:
			group_container.append({'N':N,'L':L,'senders':sender,'times':time,'pre':pre,'post':post,'delay':delay,'layer':layer})	
	senders=[i[0]-1 for i in spikes]
	times=[i[1] for i in spikes]
	print(0.0 in senders)
	found=False
	for group in group_container:
		maximum=0
		for s,t in zip(senders,times):
			if int(s)==group['senders'][0]:
				found,count=match_pattern(times,senders,t,s,group)
				if found:
					print('{}, {} \n {}'.format(t,s,group))
					plt.plot(group['times']+t,group['senders'],'ro')
					indexlist=[True if i in group['senders'] else False for i in senders]
					indexlist=np.array(indexlist)
					times=np.array(times)
					senders=np.array(senders)

					plt.plot(times[indexlist],senders[indexlist],'.')
					plt.xlim(t-2.0,t+group['times'][-1]+5.0)	
					plt.title('{},{}'.format(t,s))

					plt.show()
				else:
					if maximum<count and count > 0.3:
						maximum=count
						print(t,s,count,group['N'])

	
def strip_graph(line):
	N=count_neurons(line)
	L=length(line)
	senders,times=fire_times(line)
	pre,post,delay,layer=links(line)
	return N,L,senders,times,pre,post,delay,layer 

def match_pattern(times,senders,t,s,group):
	atime=int(t)
	atime_a=group['times'][0]
	aneuron=int(s)
	times=np.array(times)
	senders=np.array(senders)
	count=1
	for i,neuron in enumerate(group['senders']):
		p2=times==atime+2.0+group['times'][i]
		p1=times==atime+1.0+group['times'][i]
		p0=times==atime+group['times'][i]
		p_1=times==atime-1.0+group['times'][i]
		p_2=times==atime-2.0+group['times'][i]
		if neuron in senders[p1] or neuron in senders[p2] or neuron in senders[p0] or neuron in senders[p_1] or neuron in senders[p_2]:
			count+=1
	if group['N']*0.4<count*1.0:
		return True,count*1.0/group['N']
	else:
		return False,count*1.0/group['N']


f=open('polyall_final_stwd_izh_save.dat')
graph=f.readlines()
graph=graph[0]
plot_8(graph)
plt.show()

