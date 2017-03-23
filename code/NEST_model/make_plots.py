import numpy as np
import json
import sys
import os
import pylab as plt


def plot_8(group_data):
    fig = plt.figure("plot 8")
    ax0 = fig.add_subplot(221)
    ax1 = fig.add_subplot(222)
    ax2 = fig.add_subplot(223)
    ax3 = fig.add_subplot(224)
    
    N_list=[]
    L_list=[]
    T_list=[]
    for i, g in enumerate(group_data):
        N_list.append(int(g["N_fired"]))
    
        fired = g["fired"]
        times = []
        for j, f in enumerate(fired):
            times.append(int(f["t_fired"]))
        T_list.append(max(times)) # time span 
    
        L_list.append(int(g["L_max"])) # longest path

    ax1.hist(N_list, 100)
    ax1.set_title('# of neurons')
    ax2.hist(T_list, 100)
    ax2.set_title('time span[ms]')
    ax3.hist(L_list, 30)
    ax3.set_title('length of longest path')
    
    
with open(sys.argv[1], "r") as f:
    json_groups = json.load(f)

plot_8(json_groups)
plt.show()

