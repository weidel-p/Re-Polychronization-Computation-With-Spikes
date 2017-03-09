import sys
#import helper as hf
import numpy as np
import os
import nest
import matplotlib.pyplot as plt
from params import *

def write_weights(ex_neuron,interval):
    conn=nest.GetConnections(ex_neuron)
    outarray=np.zeros((len(conn),4))
    source=nest.GetStatus(conn,'source')
    target=nest.GetStatus(conn,'target')
    weight=nest.GetStatus(conn,'weight')
    delay=nest.GetStatus(conn,'delay')
    outarray[:,0]=source
    outarray[:, 1] = target
    outarray[:, 2] = weight
    outarray[:, 3] = delay
    #gets rid of connections to spike detectors and inhibitory connections

    idx=np.array(target)<=800
    outarray=outarray[idx,:]
    np.savetxt('../analysis/weights_{:02}.dat'.format(interval),outarray,fmt='%d\t%d\t%f\t%d')

nest.ResetKernel()
nest.SetKernelStatus({'resolution':dt,
			'print_time':True,
			'grng_seed':1,
            'overwrite_files':True})



neuron_model='izhikevich'

nest.CopyModel(neuron_model,'inh_Izhi',{'consistent_integration':False,
					'U_m':-0.2*65.0,
					'b':0.2,
					'c':-65.0,
					'a':0.1,
					'd':2.0})
nest.CopyModel(neuron_model,'ex_Izhi',{'consistent_integration':False,
					'U_m':-0.2*65.0,
					'b':0.2,
					'c':-65.0,
					'a':0.02,
					'd':8.0})

nest.CopyModel("static_synapse","II",{'weight':-5.0,'delay':1.0})
nest.CopyModel("stdp_izh_synapse","EX",{'weight':6.})


conn_dict_inh = {'rule': 'fixed_outdegree', 'outdegree': N_syn,'multapses':True}
conn_dict_ex = {'rule': 'fixed_outdegree', 'outdegree': N_syn,'multapses':True}


ex_neuron=nest.Create('ex_Izhi',N_ex)
inh_neuron=nest.Create('inh_Izhi',N_inh)
neurons=ex_neuron+inh_neuron

nest.Connect(inh_neuron,ex_neuron,conn_dict_inh,syn_spec='II')
nest.Connect(ex_neuron,neurons,conn_dict_ex,syn_spec='EX')
delay_list=range(1,21)
delay_list=delay_list*5
delay_list=delay_list*800
delay_list=np.array(delay_list).astype(float)
nest.SetStatus(nest.GetConnections(ex_neuron),'delay',delay_list)



random_input=nest.Create('poisson_generator')
nest.SetStatus(random_input,params={'rate':1.0})

nest.Connect(random_input,neurons,'all_to_all',{'weight':20.0})

spikedetector=nest.Create("spike_detector",N_measure,params={'withgid':True,'withtime':True,'to_memory':False,'to_file':True,'label':'../data/spikes'})

nest.SetStatus([spikedetector[0]],'start',0.)
nest.SetStatus([spikedetector[0]],'stop',200000.)

nest.SetStatus(spikedetector[1:],'start',[T_measure*(j) -100.000+T_warmup for j in range(1,N_measure)])
nest.SetStatus(spikedetector[1:],'stop',[T_measure*j+100.000+T_warmup for j in range(1,N_measure)])

nest.Connect(neurons,spikedetector,'all_to_all')

nest.Simulate(T_warmup)

for interval in range(N_measure):
    nest.Simulate(T_measure)
    write_weights(neurons,interval)


