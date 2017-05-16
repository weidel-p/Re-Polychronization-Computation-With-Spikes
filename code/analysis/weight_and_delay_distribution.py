import argparse
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import helper

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str)
parser.add_argument('-n', type=str)
parser.add_argument('-wo', type=str)
parser.add_argument('-do', type=str)


args = parser.parse_args()

def weight_dist(data,c):
    weight=[i['weight'] for i in data]
    delay = [i['delay'] for i in data]
    pre = [i['pre'] for i in data]
    post = [i['post'] for i in data]
    ex_ex_w = [i['weight'] for i in data if (i['pre']<800 and i['post']<800)]
    ex_in_w = [i['weight'] for i in data if (i['pre']<800 and i['post']>800)]
    in_ex_w = [i['weight'] for i in data if (i['pre']>800 and i['post']<800)]

    plt.subplot(2,2,1)
    plt.hist(weight, bins=np.linspace(-0.5,10.5,11), histtype='step',color=c)
    plt.title('all weights')
    plt.subplot(2,2,2)
    plt.hist(ex_ex_w, bins=np.linspace(-0.5,10.5,11), histtype='step',color=c)
    plt.title('ex-ex')
    plt.subplot(2,2,3)
    plt.hist(ex_in_w, bins=np.linspace(-0.5,10.5,11), histtype='step',color=c)
    plt.title('ex-in')

    plt.subplot(2, 2, 4)

def delay_dist(data,c):
    weight=[i['weight'] for i in data]
    delay = [i['delay'] for i in data]
    pre = [i['pre'] for i in data]
    post = [i['post'] for i in data]
    ex_ex_d = [i['delay'] for i in data if (i['pre']<800 and i['post']<800)]
    ex_in_d = [i['delay'] for i in data if (i['pre']<800 and i['post']>800)]
    in_ex_d = [i['delay'] for i in data if (i['pre']>800 and i['post']<800)]

    plt.subplot(2,2,1)
    plt.hist(delay, bins=np.linspace(-0.5,20.5,22), histtype='step',color=c)
    plt.title('all weights')

    plt.subplot(2,2,2)
    plt.hist(ex_ex_d, bins=np.linspace(-0.5,20.5,22), histtype='step',color=c)
    plt.title('ex-ex')

    plt.subplot(2,2,3)
    plt.hist(ex_in_d, bins=np.linspace(-0.5,20.5,22), histtype='step',color=c)
    plt.title('ex-in')

    plt.subplot(2, 2, 4)
    plt.hist(in_ex_d, bins=np.linspace(-0.5, 20.5, 22), histtype='step', color=c)
    plt.title('in-ex')

izh_data=helper.load_json(args.i)
nest_data=helper.load_json(args.n)
weight_dist(izh_data,'r')
weight_dist(nest_data,'b')

red_patch = mpatches.Patch(color='red', label='Izhikevic Model')
blue_patch = mpatches.Patch(color='blue', label='NEST Model')


plt.legend(handles=[red_patch,blue_patch],loc=3)


plt.savefig(args.wo)
plt.close()


delay_dist(izh_data,'r')
delay_dist(nest_data,'b')
plt.legend(handles=[red_patch,blue_patch],loc=1)

plt.savefig(args.do)
plt.close()