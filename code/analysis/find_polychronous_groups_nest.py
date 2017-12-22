import json
import numpy as np
import itertools
from multiprocessing import Pool, TimeoutError 
import time
import sys

global t_sim, N, Ne, Ni, M, min_delay, max_delay, sim_resolution
global exc_conns, exc_pre, exc_post, exc_weight, exc_delay
global inh_conns, inh_pre, inh_post, inh_weight, inh_delay


in_fn = sys.argv[1]
max_num_processes = int(sys.argv[2])
sim_resolution = float(sys.argv[3])
min_delay = float(sys.argv[4])
max_delay = float(sys.argv[5])
out_fn = sys.argv[6]


# load connectivity data
#final_stdw = np.loadtxt("final_stwd_izh.dat")
with open(in_fn, "r+") as f:
    final_stdw = json.load(f)


# and select the relevant connections
# only strong exc. and all inh connections
exc_conns = np.array([final_stdw[i] for i in range(len(final_stdw)) if final_stdw[i]['weight'] > 9.5])
inh_conns = np.array([final_stdw[i] for i in range(len(final_stdw)) if final_stdw[i]['weight'] == -5])

# dissamble connecitons into components
exc_pre = np.array([int(c['pre']) for c in exc_conns])
exc_post = np.array([int(c['post']) for c in exc_conns])
exc_weight = np.array([float(c['weight']) for c in exc_conns])
exc_delay = np.array([float(c['delay']) for c in exc_conns])

inh_pre = np.array([int(c['pre']) for c in inh_conns])
inh_post = np.array([int(c['post']) for c in inh_conns])
inh_weight = np.array([float(c['weight']) for c in inh_conns])
inh_delay = np.array([float(c['delay']) for c in inh_conns])


t_sim = 1000.0  # simulate only the first second

N = 1000  # total number of neurons
Ne = 800  # number of excitatory neurons
Ni = 200  # number of inhibitory neurons
M = 100  # number of outgoing connections per neuron


def build_simulate(stim_target_gids, stim_times, stim_weights, group, t_fired):

    import nest

    global t_sim, N, Ne, Ni, M, min_delay, max_delay, sim_resolution
    global exc_conns, exc_pre, exc_post, exc_weight, exc_delay
    global inh_conns, inh_pre, inh_post, inh_weight, inh_delay

    nest.ResetKernel()
    nest.sr("M_ERROR setverbosity")
    nest.SetKernelStatus({'resolution': sim_resolution})

    # build all neurons but only selected connections exc_conns, inh_conns

    # set default values of izhikevich neuron model
    # that excitatory and inhibitory neurons have in common
    nest.SetDefaults('izhikevich', {'b':                       0.2,
                                    'c': -65.0,
                                    'V_m': -70.0,
                                    'U_m': -70.0 * 0.2,
                                    'V_th':                   30.0,
                                    'consistent_integration': False})

    # create excitatory and inhibitory neurons and set the parameters
    # that excitatory and inhibitory neurons do not have in common
    exc_neurons = nest.Create('izhikevich', Ne, {'a': 0.02, 'd': 8.0})
    inh_neurons = nest.Create('izhikevich', Ni, {'a': 0.1,  'd': 2.0})

    # create list with global ids of all neurons
    all_neurons = exc_neurons + inh_neurons

    # every spike_generator is responsible for a specific stimulation time in [sim_resolution, max_delay]
    # create a spike generator for each stim time
    stim_times_unique = np.unique(stim_times)
    sgs = dict(zip(stim_times_unique, nest.Create('spike_generator', len(stim_times_unique))))
    # and connect it to the respective targets using the corresponding weights
    for t_stim in sgs.keys():
        nest.SetStatus([sgs[t_stim]], {"spike_times": [t_stim]})
        idxs = np.where(stim_times == t_stim)[0]
        if idxs.size:
            nest.Connect(np.array(len(idxs) * [sgs[t_stim]], np.int64), stim_target_gids[idxs], {'rule': 'one_to_one'}, syn_spec={
                         'model': 'static_synapse', "weight": stim_weights[idxs], "delay": len(idxs) * [min_delay]})

    # create spike detectors for excitatory and inhibitory neurons
    sd = nest.Create('spike_detector', 1, {'to_file': False, 'label': 'spikes'})

    # create excitatory connections
    nest.Connect(exc_pre, exc_post, {'rule': 'one_to_one'},
                 syn_spec={'model': 'static_synapse', 'weight': exc_weight, 'delay': exc_delay})

    # create inhibitory connections
    nest.Connect(inh_pre, inh_post, {'rule': 'one_to_one'},
                 syn_spec={'model': 'static_synapse', 'weight': inh_weight, 'delay': inh_delay})

    # get all connections
    connections = nest.GetConnections(all_neurons, all_neurons)

    # connect neurons to spike detector
    nest.Connect(all_neurons, sd, 'all_to_all')

    # simulate for sim_time in steps of rec_time
    nest.Simulate(t_sim)

    # extract spike times and corresponding global ids from spike detectors
    t_fired.extend(nest.GetStatus(sd, 'events')[0]['times'])
    group.extend(nest.GetStatus(sd, 'events')[0]['senders'])

    # find the links and determine the layers
    N_fired = len(group)
    L_max = 0
    links = []
    for i in range(3, N_fired):
        for j in range(i):
            if group[j] <= Ne:
                delays = exc_delay[np.where(np.all([exc_pre == group[j], exc_post == group[i]], axis=0))[0]]
            else:
                delays = inh_delay[np.where(np.all([inh_pre == group[j], inh_post == group[i]], axis=0))[0]]
            for d in delays:
                layer = 2
                if links:
                    idxs = np.where(np.array(links)[:, 1] == group[j])[0]
                    if idxs.size:
                        layer = int(np.max(np.array(links)[idxs, 3]) + 1)
                        if layer > L_max:
                            L_max = layer
                links.append([group[j], group[i], d, layer])

    if L_max >= 7:
        # save group in JSON format
        json_group = {}
        json_group["N_fired"] = N_fired
        json_group["L_max"] = L_max

        json_fired = []
        for i in range(N_fired):
            json_fire = {}
            json_fire["neuron_id"] = group[i]
            json_fire["t_fired"] = t_fired[i]
            json_fired.append(json_fire)
        json_group["fired"] = json_fired

        json_links = []
        for j in range(len(links)):
            json_link = {}
            json_link["pre"] = links[j][0]
            json_link["post"] = links[j][1]
            json_link["delay"] = links[j][2]
            json_link["layer"] = links[j][3]
            json_links.append(json_link)
        json_group["links"] = json_links

        print("group found", json_group)
        return json_group

    return None


# for every excitatory neuron and each possible triplet of excitatory presynaptic neurons
# define the connections that are initially activated and trigger the simulation
def worker(pivot_neuron):

    global t_sim, N, Ne, Ni, M, min_delay, max_delay, sim_resolution
    global exc_conns, exc_pre, exc_post, exc_weight, exc_delay
    global inh_conns, inh_pre, inh_post, inh_weight, inh_delay

    local_json_data = []

    print(pivot_neuron)

    inc_exc_conns = exc_conns[np.where(exc_post == pivot_neuron)[0]]
    for stim_triplet in itertools.combinations(inc_exc_conns, 3):
        stim_target_gids = []
        stim_times = []
        stim_weights = []
        group = []
        t_fired = []
        max_delay_triplet = np.max(np.array([c['delay'] for c in stim_triplet]))
        for st in sorted(stim_triplet, key=lambda x: x['delay'], reverse=True):
            # determine the initially activated connections
            stim_conns = exc_conns[np.where(np.all([exc_pre == st['pre'], exc_delay >= st['delay']], axis=0))[0]]

            stim_pre = np.array([int(c['pre']) for c in stim_conns])
            stim_post = np.array([int(c['post']) for c in stim_conns])
            stim_weight = np.array([float(c['weight']) for c in stim_conns])
            stim_delay = np.array([float(c['delay']) for c in stim_conns])

            stim_offset = max_delay_triplet - st['delay']
            stim_target_gids.extend(stim_post)
            stim_times.extend(stim_offset + stim_delay)
            stim_weights.extend(stim_weight)
            # store triplet as first three neurons that fire in this group
            group.append(int(st['pre']))
            t_fired.append(stim_offset)

        json_group = build_simulate(np.array(stim_target_gids), np.array(
            stim_times), np.array(stim_weights), group, t_fired)
        if not json_group == None:
            local_json_data.append(json_group)

    return local_json_data


json_data = []

pool = Pool(processes=max_num_processes)

for found_groups in pool.imap_unordered(worker, range(1, Ne+1)):
    json_data += found_groups

with open(out_fn, "w+") as f:
    json.dump(json_data, f)

