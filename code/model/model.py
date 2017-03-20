import nest
from params import *
import json

def write_weights(ex_neuron,fname):
    json_data = []
    for n_ex in ex_neuron:
        conns = nest.GetConnections([n_ex], ex_neuron + inh_neuron)

        for c in conns:
            json_conn = {}
            json_conn["pre"] = nest.GetStatus([c], "source")[0]
            json_conn["post"] = nest.GetStatus([c], "target")[0]
            json_conn["delay"] = nest.GetStatus([c], "delay")[0]
            json_conn["weight"] = nest.GetStatus([c], "weight")[0]
            json_data.append(json_conn)

    with open(fname, "w") as f:
        json.dump(json_data, f)



nest.ResetKernel()
nest.SetKernelStatus({'resolution':dt,
			'print_time':True,
			'grng_seed':2,
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

spikedetector=nest.Create("spike_detector",params={
    'withgid':True,
    'withtime':True,
    'to_memory':False,
    'to_file':True,
    'label':'../../data/spikes'})



nest.Connect(neurons,spikedetector,'all_to_all')

write_weights(neurons, '../../data/all_{}.json'.format(0))
T_interval=T_measure/N_measure
for interval in range(1,N_measure+1):
    nest.Simulate(T_interval)
    write_weights(neurons,'../../data/all_{}.json'.format(interval))

