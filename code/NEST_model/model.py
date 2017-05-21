import nest
import json
import os,sys
import argparse
sys.path.insert(0, 'code/analysis/') #ugly but not sure how to otherwise handle this
from params import *
import helper

parser = argparse.ArgumentParser()
parser.add_argument('-o', type=str)
parser.add_argument('-r','--reproduce', type=str)
parser.add_argument('-s','--stimulus', type=str)

args = parser.parse_args()

print args

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


def connect_network(ex_neuron,inh_neuron,reproduce=None):
    print reproduce
    if reproduce is None:
        conn_dict_inh = {'rule': 'fixed_outdegree', 'outdegree': N_syn, 'multapses': False, 'autapses': False}
        conn_dict_ex = {'rule': 'fixed_outdegree', 'outdegree': N_syn, 'multapses': False, 'autapses': False}
        nest.Connect(inh_neuron, ex_neuron, conn_spec=conn_dict_inh, syn_spec='II')
        nest.Connect(ex_neuron, neurons, conn_spec=conn_dict_ex, syn_spec='EX')
        delay_list =[[j for i in range(5)] for j in range(1,21)]
        delay_list = np.reshape(np.array(delay_list).astype(float),(1,100))[0]
        for n in ex_neuron:
            nest.SetStatus(nest.GetConnections(source=[n]), 'delay', delay_list)
    else:

        file=helper.load_json(reproduce)
        delay = np.array([float(i['delay']) for i in file])
        pre = np.array([i['pre'] for i in file])
        post = np.array([i['post'] for i in file])
        print delay,np,min(delay),np,max(delay)
        for pre_neuron in np.unique(pre):
            if pre_neuron in ex_neuron:
                nest.Connect([pre_neuron],post[pre_neuron==pre].tolist(),conn_spec='all_to_all',syn_spec='EX')
                conns=nest.GetConnections(source=[pre_neuron],target=post[pre_neuron==pre].tolist() )
                nest.SetStatus(conns,'delay',delay[pre_neuron==pre].tolist())
            elif pre_neuron in inh_neuron:
                nest.Connect([pre_neuron],post[pre_neuron==pre].tolist(),conn_spec= 'all_to_all',syn_spec='II')


def set_stimulus(neurons,stimulus):
    if stimulus is None:
        random_input = nest.Create('poisson_generator')
        nest.SetStatus(random_input, params={'rate': 1.0})

        nest.Connect(random_input, neurons, 'all_to_all', {'weight': 20.0})
    else:
        stimulus=np.loadtxt(stimulus)
        stim_id=stimulus[:,0]
        stim_t = stimulus[:, 1]-1
        stim_t=stim_t[stim_t>1]
        stim_id=stim_id[stim_t>1]
        print stim_id
        random_input = nest.Create('spike_generator',len(neurons))
        nest.Connect(random_input,neurons,'one_to_one')
        nest.SetStatus(nest.GetConnections(random_input),'weight',20.0)

        for i in np.unique(stim_id):
            print 'stimulut for id ',i
            idx=stim_id==i
            times=stim_t[idx]
            print times,int(i-1)
            nest.SetStatus([random_input[int(i-1)]],{'spike_times':times})


nest.ResetKernel()
nest.SetKernelStatus({'resolution': dt,
                      'print_time': True,
                      'grng_seed': 2,
                      'overwrite_files': True})

neuron_model = 'izhikevich'

nest.CopyModel(neuron_model, 'inh_Izhi', {'consistent_integration': False,
                                          'U_m': -0.2 * 65.0,
                                          'b': 0.2,
                                          'c': -65.0,
                                          'a': 0.1,
                                          'd': 2.0})
nest.CopyModel(neuron_model, 'ex_Izhi', {'consistent_integration': False,
                                         'U_m': -0.2 * 65.0,
                                         'b': 0.2,
                                         'c': -65.0,
                                         'a': 0.02,
                                         'd': 8.0})

nest.CopyModel("static_synapse", "II", {'weight': -5.0,'delay':1.0})
nest.CopyModel("stdp_izh_synapse", "EX", {'weight': 6.,'consistent_integration':False})

ex_neuron = nest.Create('ex_Izhi', N_ex)
inh_neuron = nest.Create('inh_Izhi', N_inh)
neurons = ex_neuron + inh_neuron
V_m=-65.
nest.SetStatus(neurons,'V_m',V_m)
nest.SetStatus(neurons,'U_m',0.2*V_m)

connect_network(ex_neuron,inh_neuron,reproduce=args.reproduce)
set_stimulus(neurons,args.stimulus)




spikedetector = nest.Create("spike_detector", params={
    'start':0.,
    'withgid': True,
    'withtime': True,
    'to_memory': False,
    'to_file': True,
    'label': os.path.join(args.o,prefix+'_spikes')})

nest.Connect(neurons, spikedetector, 'all_to_all')
if args.reproduce is not None:
    mm = nest.Create("multimeter", params={
        'record_from':['V_m','U_m'],
        'withgid': True,
        'withtime': True,
        'to_memory': False,
        'to_file': True,
        'label': os.path.join(args.o,prefix+'_test_single_neuron')})

    nest.Connect(mm,neurons[0:2]+neurons[-2:], 'all_to_all')

write_weights(neurons, os.path.join(args.o,prefix+'_all_{:02d}.json'.format(0)))
T_interval = T_measure / N_measure
for interval in range(1, N_measure + 1):
    nest.Simulate(5000.)
    write_weights(neurons, os.path.join(args.o,prefix+'_all_{:02d}.json'.format(interval)))
