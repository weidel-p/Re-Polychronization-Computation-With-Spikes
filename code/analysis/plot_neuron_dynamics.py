import matplotlib
matplotlib.use('Agg')
import nest
from nest import voltage_trace as vtr
import numpy as np
import pylab as plt
import seaborn as sns
import argparse

sns.set_context('paper', font_scale=3.5, rc={"lines.linewidth": 3.5})
sns.set_style('whitegrid', {"axes.linewidth": 3.5})
plt.rcParams['font.weight'] = 'bold'

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', nargs='+', type=str)
parser.add_argument('-o', '--output', type=str)

args = parser.parse_args()

neuron_params_low_res = {'consistent_integration': False,
                         'V_th': 30.,
                         'U_m': -0.2 * 65.0,
                         'b': 0.2,
                         'c': -65.0,
                         'a': 0.02,
                         'd': 8.0,
                         'I_e': 4.,
                         'integration_steps': 1}

neuron_params_high_res = {'consistent_integration': False,
                          'V_th': 30.,
                          'U_m': -0.2 * 65.0,
                          'b': 0.2,
                          'c': -65.0,
                          'a': 0.02,
                          'd': 8.0,
                          'I_e': 4.,
                          'integration_steps': 10}


# run low resolution simulation
nest.ResetKernel()
nest.SetKernelStatus({'resolution': 1.0})

neuron_low_res = nest.Create("izhikevich", 1, neuron_params_low_res) 
neuron_high_res = nest.Create("izhikevich", 1, neuron_params_high_res) 

mm = nest.Create('multimeter', 1, {'record_from': ['V_m'], 'interval': 1.0})
sd = nest.Create('spike_detector', 1)

nest.Connect(neuron_low_res, sd)
nest.Connect(neuron_high_res, sd)

nest.Connect(mm, neuron_low_res + neuron_high_res)

nest.Simulate(2000.)

ev = nest.GetStatus(sd, 'events')[0]

neuron0_mask = np.where(ev['senders'] == 1)[0]
neuron1_mask = np.where(ev['senders'] == 2)[0]

neuron0_times = ev['times'][neuron0_mask] 
neuron1_times = ev['times'][neuron1_mask]

isi0 = np.diff(neuron0_times)
isi1 = np.diff(neuron1_times)

var0 = np.var(isi0)
var1 = np.var(isi1)

mean0 = np.mean(isi0)
mean1 = np.mean(isi1)

print("isi 0", var0/mean0, 1./mean0)
print("isi 1", var1/mean1, 1./mean1)


fig = plt.figure(figsize=[16, 10])

vtr.from_device(mm)




# run high resolution simulation
nest.ResetKernel()
nest.SetKernelStatus({'resolution': 0.1})

neuron_low_res = nest.Create("izhikevich", 1, neuron_params_low_res) 

mm = nest.Create('multimeter', 1, {'record_from': ['V_m'], 'interval': 0.1})
sd = nest.Create('spike_detector', 1)

nest.Connect(neuron_low_res, sd)

nest.Connect(mm, neuron_low_res)

nest.Simulate(2000.)

ev = nest.GetStatus(sd, 'events')[0]

neuron0_mask = np.where(ev['senders'] == 1)[0]

neuron0_times = ev['times'][neuron0_mask] 

isi0 = np.diff(neuron0_times)

var0 = np.var(isi0)

mean0 = np.mean(isi0)

print("isi 0", var0/mean0, 1./mean0)



vtr.from_device(mm)

ax = fig.get_axes()[0]

handles, labels = ax.get_legend_handles_labels()

plt.legend(handles, ["1ms, 1 step", "1ms, 10 steps", "0.1ms, 1 step"], loc='best')

plt.savefig(args.output)







