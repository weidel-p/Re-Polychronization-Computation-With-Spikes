import json
import numpy as np
import itertools
from multiprocessing import Pool, TimeoutError 
import time
import sys
import nest
import copy

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


#def build_simulate(stim_target_gids, stim_times, stim_weights, stim_delay, group, t_fired, sd):

def create_network():

    print("CREATE NETWORK")

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


    return [exc_neurons, inh_neurons, sd]



# for every excitatory neuron and each possible triplet of excitatory presynaptic neurons
# define the connections that are initially activated and trigger the simulation
def worker(pivot_neuron):

    import nest

    global t_sim, N, Ne, Ni, M, min_delay, max_delay, sim_resolution
    global exc_conns, exc_pre, exc_post, exc_weight, exc_delay
    global inh_conns, inh_pre, inh_post, inh_weight, inh_delay



    local_json_data = []

    sgs = None

    inc_exc_conns = exc_conns[np.where(exc_post == pivot_neuron)[0]]
    #print("exc conns", inc_exc_conns)
    for stim_triplet_id, stim_triplet in enumerate(itertools.combinations(inc_exc_conns, 3)):


        #if not stim_triplet[0]['pre'] in [151, 527, 684]:
        #    continue
        #if not stim_triplet[1]['pre'] in [151, 527, 684]:
        #    continue
        #if not stim_triplet[2]['pre'] in [151, 527, 684]:
        #    continue

        if stim_triplet_id % 100 == 0:
            print("progress", pivot_neuron, stim_triplet_id, float(stim_triplet_id) / len(list(itertools.combinations(inc_exc_conns, 3))))
            exc_neurons, inh_neurons, sd = create_network()
            sgs = None


        #print(" STIM TRIP", pivot_neuron, stim_triplet)
        stim_target_gids = []
        stim_times = []
        stim_weights = []

        group = []
        t_fired = []


        group_delays = []
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
            #print("extend t stim", stim_offset+1-1)
            t_fired.append(stim_offset+1)
            group_delays.append(st['delay'])
            order = np.argsort(group)
            sorted_group = np.array(group)[order].tolist()
            sorted_t_fired = np.array(t_fired)[order].tolist()
            sorted_stim_delay = np.array(group_delays)[order].tolist()


            nest.SetStatus(exc_neurons + inh_neurons, {'b':                       0.2,
                                            'c': -65.0,
                                            'V_m': -70.0,
                                            'U_m': -70.0 * 0.2,
                                            'V_th':                   30.0,
                                            'consistent_integration': False})
        
            nest.SetStatus(exc_neurons, {'a': 0.02, 'd': 8.0})
            nest.SetStatus(inh_neurons, {'a': 0.1,  'd': 2.0})

        stim_target_gids = np.array(stim_target_gids)
        stim_times = np.array(stim_times)
        stim_weights = np.array(stim_weights)
        stim_delay = np.array(sorted_stim_delay)
        group = sorted_group
        t_fired = sorted_t_fired

        t_last = 61 
 

        #### STIM AND FIND GROUPS ###

        nest.ResetNetwork()
        nest.SetKernelStatus({"time": 0.0})

        # every spike_generator is responsible for a specific stimulation time in [sim_resolution, max_delay]
        # create a spike generator for each stim time

        if not sgs == None:
            nest.SetStatus(list(sgs.values()), {"spike_times": []})

        stim_times_unique = np.unique(stim_times)
        sgs = dict(zip(stim_times_unique, nest.Create('spike_generator', len(stim_times_unique))))
        # and connect it to the respective targets using the corresponding weights
        for t_stim in sgs.keys():
            #print("TSTIM", t_stim)
            nest.SetStatus([sgs[t_stim]], {"spike_times": [t_stim]})
            idxs = np.where(stim_times == t_stim)[0]
            if idxs.size:
                nest.Connect(np.array(len(idxs) * [sgs[t_stim]], np.int64), stim_target_gids[idxs], {'rule': 'one_to_one'}, syn_spec={
                             'model': 'static_synapse', "weight": stim_weights[idxs], "delay": len(idxs) * [min_delay]})

        #print(zip(stim_target_gids, stim_times))
        N_postspikes = np.zeros(1000).astype('int')
        I_postspikes = np.zeros([1000, 1000])
        J_postspikes = np.zeros([1000, 1000])
        D_postspikes = np.zeros([1000, 1000])
        C_postspikes = np.zeros([1000, 1000])
        #print(group, stim_delay, t_fired)

        for i, t in enumerate(t_fired):
            for d in range(21):
                idxs = np.where(np.logical_and(exc_pre == group[i], exc_delay == d))[0]
                for j, p in enumerate(exc_post[idxs].astype('int')):

                    if (exc_weight[idxs][j] > 9.5 or p > Ne) and d >= stim_delay[i]:
                        timing = int(t + d) -1 ### WHY +1

                        J_postspikes[timing][N_postspikes[timing]] = group[i]
                        I_postspikes[timing][N_postspikes[timing]] = p 
                        D_postspikes[timing][N_postspikes[timing]] = d 
                        C_postspikes[timing][N_postspikes[timing]] = exc_weight[idxs][j]
                        N_postspikes[timing] += 1

                        t_last = max(t_last, timing+1)

                        #print("timing", timing, "t", t, "J", J_postspikes[timing][N_postspikes[timing]-1]-1, "D", D_postspikes[timing][N_postspikes[timing]-1]-1, "C", C_postspikes[timing][N_postspikes[timing]-1], "I", I_postspikes[timing][N_postspikes[timing]-1]-1, "N", N_postspikes[timing])


        # simulate for sim_time in steps of rec_time
        nest.Simulate(t_sim)

        # extract spike times and corresponding global ids from spike detectors
        t_fired.extend(nest.GetStatus(sd, 'events')[0]['times'])
        group.extend(nest.GetStatus(sd, 'events')[0]['senders'])

        all_t_fired = copy.deepcopy(t_fired)
        all_group = copy.deepcopy(group)

        relevant_spikes = np.where(np.array(all_t_fired) < t_last)[0]
        t_fired = np.array(all_t_fired)[relevant_spikes].tolist()
        group = np.array(all_group)[relevant_spikes].tolist()

        i = 2 

        #for i, t in enumerate(t_fired):
        while t <= t_last+1 and i+1 < len(t_fired) and len(t_fired) < 1000:


            i += 1
            t = t_fired[i]

            relevant_spikes = np.where(np.array(all_t_fired) <= t_last + 1)[0]
            t_fired = np.array(all_t_fired)[relevant_spikes].tolist()
            group = np.array(all_group)[relevant_spikes].tolist()

            if len(t_fired) >= 1000:
                continue


            #print("SPIKE at ", t, "id", group[i], "t_last", t_last, all_t_fired)
            for d in range(21):


                if group[i] <= Ne:
                    idxs = np.where(np.logical_and(exc_pre == group[i], exc_delay == d))[0]
                    for j, p in enumerate(exc_post[idxs].astype('int')):


                        if (exc_weight[idxs][j] > 9.5 or p > Ne):

                            # TODO check this. this could be wrong
                            if N_postspikes[timing] >= 1000:
                                continue

                            timing = int(t + d) -1 ### WHY +1

                            J_postspikes[timing][N_postspikes[timing]] = group[i]
                            I_postspikes[timing][N_postspikes[timing]] = p 
                            D_postspikes[timing][N_postspikes[timing]] = d 
                            C_postspikes[timing][N_postspikes[timing]] = exc_weight[idxs][j]
                            N_postspikes[timing] += 1

                            t_last = max(t_last, timing+1)

                            #print("SIM timing", timing, "t", t, "J", J_postspikes[timing][N_postspikes[timing]-1]-1, "D", D_postspikes[timing][N_postspikes[timing]-1]-1, "C", C_postspikes[timing][N_postspikes[timing]-1], "I", I_postspikes[timing][N_postspikes[timing]-1]-1, "N", N_postspikes[timing])
                else:

                    idxs = np.where(np.logical_and(inh_pre == group[i], inh_delay == d))[0]
                    for j, p in enumerate(inh_post[idxs].astype('int')):

                        #print("INHIBITORY", idxs, group[i], d, p#, np.where(inh_delay == d)[0], np.where(inh_pre == group[i])[0])

                        # TODO check this. this could be wrong
                        if N_postspikes[timing] >= 1000:
                            continue

                        timing = int(t + d) -1 ### WHY +1
                            

                        J_postspikes[timing][N_postspikes[timing]] = group[i]
                        I_postspikes[timing][N_postspikes[timing]] = p 
                        D_postspikes[timing][N_postspikes[timing]] = d 
                        C_postspikes[timing][N_postspikes[timing]] = inh_weight[idxs][j]
                        N_postspikes[timing] += 1


                        t_last = max(t_last, timing+1)

                        #print("SIM timing INHIBITORY!!!", timing, "t", t, "J", J_postspikes[timing][N_postspikes[timing]-1]-1, "D", D_postspikes[timing][N_postspikes[timing]-1]-1, "C", C_postspikes[timing][N_postspikes[timing]-1], "I", I_postspikes[timing][N_postspikes[timing]-1]-1, "N", N_postspikes[timing])


        if t_last > t_sim:
            print("ERROR: simtime not sufficient", t_sim, t_last)



        layer = [1] * len(group)

        # find the links and determine the layers
        N_fired = len(group)
        L_max = 0
        links = []
        json_group = None
        #print(t_fired)
        #print("N Fired", N_fired)

        if N_fired > 6:
            for i, t in enumerate(t_fired):
                t -= 1
                if i < 3:
                    continue
                layer[i] = 0
                #print("I", i, "T", t)
#               for ( p=t_fired[i]; (p>t_fired[i]-latency) & (p>=0); p-- ) // latency=D=20
                for p in np.arange(t, t-20, -1).astype('int'):
                    if p < 0:
                        break

                    #print("P", p, " len N postspikes", N_postspikes[p])
                    
#                 for ( j=0; j<N_postspikes[p]; j++ )
                    for j in range(N_postspikes[p]):
                        #print("J", j)
#                   if ( (I_postspikes[p][j]==group[i]) & (J_postspikes[p][j]<Ne) )
#                   {

                        if (I_postspikes[p][j]==group[i]) and (J_postspikes[p][j]<Ne):
#                     for ( k=0; k<i; k++ )
#                    {
#               	    if ( (group[k]==J_postspikes[p][j]) & (layer[k]+1>layer[i]) ){
#               	      layer[i]=layer[k]+1;
#
#                    }
#                    }
                            for k in range(i):
                                if group[k] == J_postspikes[p][j] and layer[k]+1 > layer[i]:
                                    layer[i] = layer[k]+1

                                    if layer[i] > L_max:
                                        L_max = layer[i]


                            links.append([J_postspikes[p][j], I_postspikes[p][j], D_postspikes[p][j], layer[i]])
                            #print("new link", t, J_postspikes[p][j], I_postspikes[p][j], D_postspikes[p][j], layer[i])



#                       {
#
#               	  links[N_links][0]=J_postspikes[p][j];
#               	  links[N_links][1]=I_postspikes[p][j];
#               	  links[N_links][2]=D_postspikes[p][j];
#               	  links[N_links++][3]=layer[i];
#               	  if ( L_max < layer[i] )
#               	  L_max = layer[i];
#                     }

                

   #         for i in range(3, N_fired):
   #             for j in range(i):
   #                 if group[j] <= Ne:
   #                     delays = exc_delay[np.where(np.all([exc_pre == group[j], exc_post == group[i]], axis=0))[0]]
   #                 else:
   #                     delays = inh_delay[np.where(np.all([inh_pre == group[j], inh_post == group[i]], axis=0))[0]]
   #                 for d in delays:
   #                     layer = 2
   #                     if links:
   #                         idxs = np.where(np.array(links)[:, 1] == group[j])[0]
   #                         if idxs.size:
   #                             layer = int(np.max(np.array(links)[idxs, 3]) + 1)
   #                             if layer > L_max:
   #                                 L_max = layer
   #                     links.append([group[j], group[i], d, layer])


            if L_max >= 7:
                # save group in JSON format
                json_group = {}
                json_group["N_fired"] = N_fired
                json_group["L_max"] = L_max

                json_fired = []
                for i in range(N_fired):
                    json_fire = {}
                    json_fire["neuron_id"] = int(group[i]) - 1
                    json_fire["t_fired"] = float(t_fired[i]) - 1
                    json_fired.append(json_fire)
                json_group["fired"] = json_fired

                json_links = []
                for j in range(len(links)):
                    json_link = {}
                    json_link["pre"] = int(links[j][0])-1
                    json_link["post"] = int(links[j][1])-1
                    json_link["delay"] = float(links[j][2])-1
                    json_link["layer"] = int(links[j][3])
                    json_links.append(json_link)
                json_group["links"] = json_links

                print("group found", json_group["N_fired"], json_group["L_max"])

                for f in json_group['fired']:
                    print(f)
                for l in json_group['links']:
                    print(l)
        
        #json_group = build_simulate(np.array(stim_target_gids), np.array(
        #    stim_times), np.array(stim_weights), np.array(sorted_stim_delay), sorted_group, sorted_t_fired, sd)
        if not json_group == None:
            local_json_data.append(json_group)

    return local_json_data


json_data = []

pool = Pool(processes=max_num_processes)

for found_groups in pool.imap_unordered(worker, range(1, 41)):# Ne+1)):
    json_data += found_groups

with open(out_fn, "w+") as f:
    json.dump(json_data, f)


stwd_data = []
for c in final_stdw:
    stwd_data.append([c['pre'], c['post'], c['weight'], c['delay']]) 

np.savetxt("stwd_data.dat", stwd_data) 

