import nest
from params import *
import json
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', type=str)
args = parser.parse_args()


def write_weights(neuron, fname):
    json_data = []
    for n in neuron:
        conns = nest.GetConnections([n], neuron)

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
nest.SetKernelStatus({'resolution': dt,
                      'print_time': True,
                      'grng_seed': 2,
                      'overwrite_files': True})

neuron_model = 'izhikevich'

nest.CopyModel(neuron_model, 'inh_Izhi', inh_neuron_model)
nest.CopyModel(neuron_model, 'ex_Izhi' , exc_neuron_model)

nest.CopyModel("static_synapse", "II", {'weight': -5.0, 'delay': 1.0})
nest.CopyModel("stdp_izh_synapse", "EX", {'weight': 6.,'consistent_integration':False})


ex_neuron = nest.Create('ex_Izhi',2)
inh_neuron = nest.Create('inh_Izhi', 2)
neurons = ex_neuron + inh_neuron
# V_m=-65.+np.random.uniform(0,10,len(neurons))
# nest.SetStatus(neurons,'V_m',V_m)
#
# nest.SetStatus(neurons,'U_m',0.2*V_m)
nest.Connect(ex_neuron, ex_neuron[::-1], 'one_to_one', syn_spec='EX')
nest.Connect(ex_neuron, inh_neuron, 'all_to_all', syn_spec='EX')

nest.Connect(inh_neuron, ex_neuron, 'all_to_all', syn_spec='II')
# delay_list = range(1, 21)
# delay_list = delay_list * 5
# delay_list = delay_list * 800
# delay_list = np.array(delay_list).astype(float)
# nest.SetStatus(nest.GetConnections(ex_neuron), 'delay', delay_list)

spk_gen=nest.Create('spike_generator',4)
nest.SetStatus([spk_gen[0]],{'spike_times':[100.]})
nest.SetStatus([spk_gen[1]],{'spike_times':[200.]})
nest.SetStatus([spk_gen[2]],{'spike_times':[300.]})
nest.SetStatus([spk_gen[3]],{'spike_times':[400.]})


nest.Connect(spk_gen, neurons, 'one_to_one', {'weight': 20.0})

mm = nest.Create("multimeter", params={
    'record_from':['V_m'],
    'withgid': True,
    'withtime': True,
    'to_memory': False,
    'to_file': True,
    'label': os.path.join(args.o,prefix+'_mem_test')})

nest.Connect(mm,neurons[0:2]+neurons[-2:], 'all_to_all')

nest.Simulate(1000.)
