import matplotlib
matplotlib.use('Agg')
import nest
from nest import voltage_trace as vtr
import numpy as np
import pylab as plt
import seaborn as sns
import argparse
import plot_helper as phf
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid.inset_locator import inset_axes



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
                         'integration_steps': 1}

neuron_params_high_res = {'consistent_integration': False,
                          'V_th': 30.,
                          'U_m': -0.2 * 65.0,
                          'b': 0.2,
                          'c': -65.0,
                          'a': 0.02,
                          'd': 8.0,
                          'integration_steps': 10}


# run low resolution simulation
nest.ResetKernel()
nest.SetKernelStatus({'resolution': 1.0})

neuron_low_res = nest.Create("izhikevich", 1, neuron_params_low_res) 
neuron_high_res = nest.Create("izhikevich", 1, neuron_params_high_res) 

nest.SetStatus(neuron_low_res, {"I_e": 4.})
nest.SetStatus(neuron_high_res, {"I_e": 4.})

mm = nest.Create('multimeter', 1, {'record_from': ['V_m', 'U_m'], 'interval': 1.0})
sd = nest.Create('spike_detector', 1)

nest.Connect(neuron_low_res, sd)
nest.Connect(neuron_high_res, sd)

nest.Connect(mm, neuron_low_res + neuron_high_res)

nest.Simulate(1000.)

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

ev_mm = nest.GetStatus(mm, 'events')[0]
senders = ev_mm['senders']
times = ev_mm['times']
vms = ev_mm['V_m']
ums = ev_mm['U_m']

mask_low = np.where(senders == neuron_low_res)[0]
mask_high = np.where(senders == neuron_high_res)[0]

Vs_current_low_low = vms[mask_low] 
Vs_current_low_high = vms[mask_high] 

Us_current_low_low = ums[mask_low] 
Us_current_low_high = ums[mask_high] 

times_current_low_low = times[mask_low]
times_current_low_high = times[mask_high]




# run high resolution simulation
nest.ResetKernel()
nest.SetKernelStatus({'resolution': 0.1})

neuron_low_res = nest.Create("izhikevich", 1, neuron_params_low_res) 

nest.SetStatus(neuron_low_res, {"I_e": 4.})

mm = nest.Create('multimeter', 1, {'record_from': ['V_m', 'U_m'], 'interval': 0.1})
sd = nest.Create('spike_detector', 1)

nest.Connect(neuron_low_res, sd)

nest.Connect(mm, neuron_low_res)

nest.Simulate(1000.)

ev = nest.GetStatus(sd, 'events')[0]

neuron0_mask = np.where(ev['senders'] == 1)[0]

neuron0_times = ev['times'][neuron0_mask] 

isi0 = np.diff(neuron0_times)

var0 = np.var(isi0)

mean0 = np.mean(isi0)

print("isi 0", var0/mean0, 1./mean0)

ev_mm = nest.GetStatus(mm, 'events')[0]
senders = ev_mm['senders']
times = ev_mm['times']
vms = ev_mm['V_m']
ums = ev_mm['U_m']

mask_low = np.where(senders == neuron_low_res)[0]

Vs_current_high_low = vms[mask_low] 
Us_current_high_low = ums[mask_low] 

times_current_high_low = times[mask_low]







# run high resolution simulation
nest.ResetKernel()
nest.SetKernelStatus({'resolution': 1.0})

neuron_low_res = nest.Create("izhikevich", 1, neuron_params_low_res) 
neuron_high_res = nest.Create("izhikevich", 1, neuron_params_high_res) 

sg = nest.Create("spike_generator", 1, {"spike_times": [50., 50.]})

nest.Connect(sg, neuron_low_res + neuron_high_res, 'all_to_all', {'weight': 10.})

mm = nest.Create('multimeter', 1, {'record_from': ['V_m', 'U_m'], 'interval': 1.0})
sd = nest.Create('spike_detector', 1)

nest.Connect(neuron_low_res, sd)
nest.Connect(neuron_high_res, sd)

nest.Connect(mm, neuron_low_res)
nest.Connect(mm, neuron_high_res)

nest.Simulate(100.)

ev = nest.GetStatus(sd, 'events')[0]
print(ev)


neuron0_mask = np.where(ev['senders'] == 1)[0]

neuron0_times = ev['times'][neuron0_mask] 

isi0 = np.diff(neuron0_times)

var0 = np.var(isi0)

mean0 = np.mean(isi0)

ev = nest.GetStatus(mm, 'events')[0]

print("isi 0", var0/mean0, 1./mean0)


ev_mm = nest.GetStatus(mm, 'events')[0]
senders = ev_mm['senders']
times = ev_mm['times']
vms = ev_mm['V_m']
ums = ev_mm['U_m']

mask_low = np.where(senders == neuron_low_res)[0]
mask_high = np.where(senders == neuron_high_res)[0]

Vs_spike_low_low = vms[mask_low] 
Vs_spike_low_high = vms[mask_high] 

Us_spike_low_low = ums[mask_low] 
Us_spike_low_high = ums[mask_high] 

times_spike_low_low = times[mask_low]
times_spike_low_high = times[mask_high]





# run high resolution simulation
nest.ResetKernel()
nest.SetKernelStatus({'resolution': 0.1})

neuron_low_res = nest.Create("izhikevich", 1, neuron_params_low_res) 

sg = nest.Create("spike_generator", 1, {"spike_times": [50., 50.]})

nest.Connect(sg, neuron_low_res, 'all_to_all', {'weight': 85.})

mm = nest.Create('multimeter', 1, {'record_from': ['V_m', 'U_m'], 'interval': 0.1})
sd = nest.Create('spike_detector', 1)

nest.Connect(neuron_low_res, sd)

nest.Connect(mm, neuron_low_res)

nest.Simulate(100.)

ev = nest.GetStatus(sd, 'events')[0]
print(ev)

neuron0_mask = np.where(ev['senders'] == 1)[0]

neuron0_times = ev['times'][neuron0_mask] 

isi0 = np.diff(neuron0_times)

var0 = np.var(isi0)

mean0 = np.mean(isi0)

print("isi 0", var0/mean0, 1./mean0)

ev_mm = nest.GetStatus(mm, 'events')[0]
senders = ev_mm['senders']
times = ev_mm['times']
vms = ev_mm['V_m']
ums = ev_mm['U_m']

mask_low = np.where(senders == neuron_low_res)[0]

Vs_spike_high_low = vms[mask_low] 
Us_spike_high_low = ums[mask_low] 

times_spike_high_low = times[mask_low]




def build_model(weight=10.,resolution=1.0,N_steps=1):
    nest.ResetKernel()
    print(resolution)
    nest.SetKernelStatus({'resolution': resolution,
                          'print_time': True })
    print(nest.GetStatus([0]))
    neuron_model = 'izhikevich'
    nest.CopyModel(neuron_model, 'inh_Izhi', {'consistent_integration': False,
                                              'U_m': -0.2 * 65.0,
                                              'b': 0.2,
                                              'c': -65.0,
                                              'a': 0.1,
                                              'd': 2.0,
                                              'tau_minus': 20.,
                                              'integration_steps':N_steps})
    nest.CopyModel(neuron_model, 'ex_Izhi', {'consistent_integration': False,
                                             'U_m': -0.2 * 65.0,
                                             'b': 0.2,
                                             'c': -65.0,
                                             'a': 0.02,
                                             'd': 8.0,
                                             'tau_minus': 20.,
                                             'integration_steps':N_steps})

    nest.CopyModel("static_synapse", "EX", {'weight': weight, 'delay': 1.0})

    ex_neuron = nest.Create('ex_Izhi', 1)
    spike_gen = nest.Create('spike_generator', 1)
    nest.SetStatus(spike_gen, {'spike_times': [50.]})

    mm = nest.Create("multimeter", params={
        'record_from': ['V_m','U_m'],
        'withgid': True,
        'withtime': True,
        'to_memory': True,
        'to_file': False,
        'label': 'mem_pot'})
    nest.SetStatus(ex_neuron,'V_m',-70.)
    nest.SetStatus(ex_neuron,'U_m',-70.*.2)

    nest.Connect(mm, ex_neuron, 'all_to_all')
    nest.Connect(spike_gen, ex_neuron, 'all_to_all','EX')

    nest.Simulate(100.)
    return nest.GetStatus(mm)[0]['events']

res0p1=build_model(weight=85.,resolution=0.1,N_steps=1)
res1p0=build_model(weight=10.,resolution=1.0,N_steps=1)
res1p0_high_res=build_model(weight=10.,resolution=1.0,N_steps=10)



phf.latexify(columns=2)


fig = plt.figure()
gs0 = gridspec.GridSpec(2, 3)

ax0 = plt.subplot(gs0[0, 0])
ax1 = plt.subplot(gs0[1, 0])
ax2 = plt.subplot(gs0[0, 1])
ax3 = plt.subplot(gs0[1, 1])
ax4 = plt.subplot(gs0[0, 2])
ax5 = plt.subplot(gs0[1, 2])


ax4.plot(res0p1['times'],res0p1['V_m'])
ax4.plot(res1p0['times'],res1p0['V_m'])
ax4.plot(res1p0_high_res['times'],res1p0_high_res['V_m'])
ax4.set_xticks([])

ax5.plot(res0p1['times'],res0p1['U_m'])
ax5.plot(res1p0['times'],res1p0['U_m'])
ax5.plot(res1p0_high_res['times'],res1p0_high_res['U_m'])
ax5.set_xlabel("Time [ms]")


# make insets for current input
width="30%"
height=0.4


inset_axes_0 = inset_axes(ax0, width="100%", height="100%", loc=2,
                   bbox_to_anchor=(0.18, .78,0.3,0.225), bbox_transform=ax0.transAxes)
inset_axes_2 = inset_axes(ax2,
                          width=width,  # width = 30% of parent_bbox
                          height=height,  # height : 1 inch
                          loc=1)
inset_axes_4 = inset_axes(ax4,
                          width=width,  # width = 30% of parent_bbox
                          height=height,  # height : 1 inch
                          loc=1)
print(inset_axes_0.get_position())
print(inset_axes_2.get_position())



inset_axes_0.plot([-100,-0.5,0.,1000,1000.5,1100],[0,0,4,4,0,0])
inset_axes_2.plot([45,49,50,51,52,85],[0,0,20,20,0,0])
inset_axes_4.plot([45,49,50,51,52,85],[0,0,10,10,0,0])


inset_axes_0.set_xlim([-100,1100])
inset_axes_0.set_ylim([-2,8])
inset_axes_0.set_yticks([0,4])
inset_axes_0.set_xticks([0,1000])

inset_axes_2.set_xlim([45,85])
inset_axes_2.set_ylim([-2,25])
inset_axes_2.set_yticks([0,20])
inset_axes_2.set_xticks([40.,60,80])

inset_axes_4.set_xlim([45,85])
inset_axes_4.set_ylim([-2,25])
inset_axes_4.set_yticks([0,10])
inset_axes_4.set_xticks([40.,60,80])

for ax in (inset_axes_0,inset_axes_2,inset_axes_4):
    ax.set_xticklabels([r'\small{{{}}}'.format(int(i)) for i in ax.get_xticks() ])
    ax.set_yticklabels([r'\small{{{}}}'.format(int(i)) for i in ax.get_yticks()])
    ax.set_ylabel('\small{$I_{ext}$}')

inset_axes_0.set_yticklabels([r'\small{{{}}}'.format(i) for i in inset_axes_0.get_yticks() ])

ax0.plot(times_current_low_low, Vs_current_low_low, label="low low")
ax0.plot(times_current_low_high, Vs_current_low_high, label="low high")
ax0.plot(times_current_high_low, Vs_current_high_low, label="high low")
ax0.set_ylabel("v [mV]")
ax0.set_xticks([])

ax1.plot(times_current_low_low, Us_current_low_low, label="low low")
ax1.plot(times_current_low_high, Us_current_low_high, label="low high")
ax1.plot(times_current_high_low, Us_current_high_low, label="high low")
ax1.set_ylabel("u [a.u.]")
ax1.set_xlabel("Time [ms]")

ax2.plot(times_spike_low_low, Vs_spike_low_low, label="low low")
ax2.plot(times_spike_low_high, Vs_spike_low_high, label="low high")
ax2.plot(times_spike_high_low, Vs_spike_high_low, label="high low")
ax2.set_xticks([])

ax3.plot(times_spike_low_low, Us_spike_low_low, label="low low")
ax3.plot(times_spike_low_high, Us_spike_low_high, label="low high")
ax3.plot(times_spike_high_low, Us_spike_high_low, label="high low")
ax3.set_xlabel("Time [ms]")

for ax in (ax2,ax3,ax4,ax5):
    ax.set_xlim([35,85])
    ax.set_xticks([40,60, 80])
    ax.set_ylim([-100,70])
for ax in (ax2,  ax4):
    ax.set_xlim([35, 85])
    ax.set_xticks([40, 60, 80])


ax0.set_xlim([-50,1050])
ax0.set_xticks([0,500,1000])
ax2.set_ylim([-100, 70])
ax2.set_yticks([-70, -50,0,50])

ax1.set_ylim([-16, 0])
ax1.set_yticks([-15,-10, -5])

ax3.set_ylim([-16, 0])
ax3.set_yticks([-15,-10, -5])

ax4.set_ylim([-72.5, -60])
ax.set_yticks([-70, -65])

ax5.set_ylim([-14.1, -13.8  ])
ax5.set_yticks([-14.0, -13.9  ])

gs0.update(left=0.08, right=0.99, top=0.95, bottom=0.1, hspace=0.2, wspace=0.25)
for ax, letter in [(ax0, 'A'), (ax1, 'B'), (ax2, 'C'),(ax3,'D'),(ax4, 'E'),(ax5,'F')]:
    ax.annotate(r'\textbf{{{letter}}}'.format(letter=letter), xy=(-0.15, 0.99), xycoords='axes fraction', fontsize=10,
                horizontalalignment='left', verticalalignment='top', annotation_clip=False)




plt.savefig(args.output)







