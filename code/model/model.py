import sys
sys.path.insert(0, '../Kumar_Model/')
#import helper as hf
import numpy as np
import nest
import matplotlib.pyplot as plt
import os
from params import *



nest.ResetKernel()
nest.SetKernelStatus({'resolution':dt,
			'print_time':True,
			'grng_seed':1})



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


conn_dict_inh = {'rule': 'fixed_outdegree', 'outdegree': N_syn}
conn_dict_ex = {'rule': 'fixed_outdegree', 'outdegree': N_syn}


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

measure_intervals = int(T/T_measure)+1
spikedetector=nest.Create("spike_detector",measure_intervals-1,params={'withgid':True,'withtime':True,'to_memory':True,'to_file':False,'label':'spike_15'})
nest.SetStatus(spikedetector,'start',[T_measure*(j-1) for j in range(1,measure_intervals)])
nest.SetStatus(spikedetector,'stop',[T_measure*j for j in range(1,measure_intervals)])
nest.Connect(ex_neuron,spikedetector,'all_to_all')
#path=os.path.listdir()
#for files in path:
#    if '.gdf' in files
	
nest.Simulate(T_measure)


