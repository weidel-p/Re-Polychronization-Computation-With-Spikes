import nest
import json
import os
import sys
import argparse
# ugly but not sure how to otherwise handle this
sys.path.insert(0, 'code/analysis/')
from params import *
import helper

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str)

args = parser.parse_args()

cfg = helper.parse_config(args.config)


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


def connect_network(ex_neuron, inh_neuron, conf):

    if conf["type"] == "reproduce":
        file = helper.load_json(conf["from-file"])

        delay = np.array([float(i['delay']) for i in file])
        pre = np.array([i['pre'] for i in file])
        post = np.array([i['post'] for i in file])

        for pre_neuron in np.unique(pre):
            idxes = np.where(pre_neuron == pre)[0]
            if pre_neuron in ex_neuron:

                if pre_neuron < 801:
                    nest.Connect([pre_neuron], post[idxes].tolist(),
                                 conn_spec='all_to_all', syn_spec='EX')
                else:
                    nest.Connect([pre_neuron], post[idxes].tolist(),
                                 conn_spec='all_to_all', syn_spec='EX_stat')

            elif pre_neuron in inh_neuron:
                nest.Connect([pre_neuron], post[idxes].tolist(),
                             conn_spec='all_to_all', syn_spec='II')

        for pr, po, de in zip(pre, post, delay):
            conn = nest.GetConnections(source=[pr], target=[po])
            nest.SetStatus(conn, 'delay', de)

    elif conf["type"] == "generate":

        conn_dict_inh = {'rule': 'fixed_outdegree',
                         'outdegree': N_syn, 'multapses': False, 'autapses': False}
        conn_dict_ex = {'rule': 'fixed_outdegree',
                        'outdegree': N_syn, 'multapses': False, 'autapses': False}
        nest.Connect(inh_neuron, ex_neuron,
                     conn_spec=conn_dict_inh, syn_spec='II')
        nest.Connect(ex_neuron, neurons, conn_spec=conn_dict_ex, syn_spec='EX')

        if conf["delay-distribution"] == "uniform-non-random":
            delay_list = [[j for i in range(5)] for j in range(conf["delay-range"][0], conf["delay-range"][1])]
            delay_list = np.reshape(
                np.array(delay_list).astype(float), (1, 100))[0]

        elif conf["delay-distribution"] == "uniform":
            print "Connectivity: NotImplementedError", conf["delay-distribution"]

        for n in ex_neuron:
            nest.SetStatus(nest.GetConnections(
                source=[n]), 'delay', delay_list)
    else:
        print "warning: no connectivity has been generated"



def set_stimulus(neurons, conf):
    if conf["type"] == "reproduce":
        stimulus = np.loadtxt(conf["from-file"])
        stim_id = stimulus[:, 0].astype(int)
        stim_t = stimulus[:, 1] - 1
        del stimulus
        # first neuron gets current manually rest via spike generator

        nest.SetStatus([neurons[stim_id[0]-1]], 'I', 20.)
        # otherwise stimulus must occur at -1ms
        stim_id = stim_id[stim_t > 0]
        stim_t = stim_t[stim_t > 0]
        random_input = nest.Create('spike_generator', len(neurons))
        nest.Connect(random_input, neurons, 'one_to_one')
        nest.SetStatus(nest.GetConnections(random_input), 'weight', 20.)
        for i in np.unique(stim_id):
            idx = stim_id == i
            times = stim_t[idx]
            nest.SetStatus([random_input[int(i - 1)]], {'spike_times': times})
        del stim_id
        del stim_t

    elif conf["type"] == "generate":
        if conf["distribution"] == "poisson":
            random_input = nest.Create('poisson_generator')
            nest.SetStatus(random_input, params={'rate': conf["rate"]})

            nest.Connect(random_input, neurons, 'all_to_all', {'weight': conf["weight"]})
        else:
            print "Stimulus: NotImplementedError", conf["distribution"]


    else:
        print "warning: no stimulus has been generated"


def set_initial_conditions(neurons, conf):
    if conf["type"] == "reproduce":
        initials = np.loadtxt(conf["from-file"])
        stim_id = initials[:, 0]
        stim_v = initials[:, 1]
        stim_u = initials[:, 2]
        # first neuron gets current manually rest via spike generator
        nest.SetStatus(neurons, 'V_m', stim_v)
        nest.SetStatus(neurons, 'U_m', stim_u)
    elif conf["type"] == "generate":
        if conf["distribution"] == "uniform":

            vms = np.random.uniform(conf["V_m-range"][0], conf["V_m-range"][1], len(neurons))
            ums = np.array([0.2 * v for v in vms])

            nest.SetStatus(neurons, 'V_m', vms)
            nest.SetStatus(neurons, 'U_m', ums)
        else:
            print "Init State: NotImplementedError", conf["distribution"]
    else:
        print "warning: no inital state has been generated"


nest.ResetKernel()

seed = [np.random.randint(0,9999999)]*num_threads

nest.SetKernelStatus({'resolution': cfg["simulation-params"]["resolution"],
                      'print_time': True,
                      'rng_seeds': seed,
                      'overwrite_files': True,
                      'local_num_threads': num_threads,
                      'syn_update_interval': cfg["simulation-params"]["synapse-update-interval']})

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

nest.CopyModel("static_synapse", "II", {'weight': -5.0, 'delay': 1.0})
nest.CopyModel(cfg["network-params"]["connectivity"]["synapse-model"], "EX", {
               'weight': 6., 'consistent_integration': False})
nest.CopyModel("static_synapse", "EX_stat", {'weight': 6.})

ex_neuron = nest.Create('ex_Izhi', N_ex)
inh_neuron = nest.Create('inh_Izhi', N_inh)
neurons = ex_neuron + inh_neuron

set_initial_conditions(neurons, cfg["network-params"]["initial-state"])


connect_network(ex_neuron, inh_neuron, cfg["network-params"]["connectivity"])

set_stimulus(neurons, cfg["network-params"]["stimulus"])



spikedetector = nest.Create("spike_detector", params={
    'start': cfg["simulation-params"]["sim-time"] - 10000.,
    'withgid': True,
    'withtime': True,
    'to_memory': False,
    'to_file': True,
    'label': os.path.join(cfg["simulation-params"]["data-path"], cfg["simulation-params"]["data-prefix"] + '_spikes')})

nest.Connect(neurons, spikedetector, 'all_to_all')

#if cfg["network-params"]["connectivity"]["type"] == "generate": 
mm = nest.Create("multimeter", params={
        'record_from': ['V_m', 'U_m'],
        'withgid': True,
        'withtime': True,
        'to_memory': False,
        'to_file': True,
        'precision': 17,
        # 'start':0.,
        # 'stop': 1000. * 100.,
        'label': os.path.join(cfg["simulation-params"]["data-path"], cfg["simulation-params"]["data-prefix"])})
nest.Connect(mm,[699,705,731,831], 'all_to_all')

write_weights(neurons, os.path.join(
    cfg["simulation-params"]["data-path"], cfg["simulation-params"]["data-prefix"] + '_all_{:02d}.json'.format(0)))

T_interval = cfg["simulation-params"]["sim-time"] / cfg["simulation-params"]["num-measurements"]

for interval in range(1, cfg["simulation-params"]["num-measurements"] + 1):
    nest.Simulate(T_interval)
    write_weights(neurons, os.path.join(
        cfg["simulation-params"]["data-path"], cfg["simulation-params"]["data-prefix"] + '_all_{:02d}.json'.format(interval)))



