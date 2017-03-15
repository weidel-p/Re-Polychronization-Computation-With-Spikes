import nest
from params import *
import json
def write_weights(ex_neuron,fname):
    conn=nest.GetConnections(ex_neuron)
    outarray=np.zeros((len(conn),4))
    source=np.array(nest.GetStatus(conn,'source'))
    target=np.array(nest.GetStatus(conn,'target'))
    weight=np.array(nest.GetStatus(conn,'weight'))
    delay=np.array(nest.GetStatus(conn,'delay'))
    #gets rid of connections to spike detectors and inhibitory connections

    idx=(source<=800)&(target<1001)
    out_dict=dict(
        source=source[idx].tolist(),
        target=target[idx].tolist(),
        weight=weight[idx].tolist(),
        delay=delay[idx].tolist()
    )
    f=open(fname,'w')
    json.dump(out_dict,f)






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

