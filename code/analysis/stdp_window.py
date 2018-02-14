import nest
import numpy as np
import sys
import helper
import json
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str)
parser.add_argument('-o', '--output', type=str)
parser.add_argument('-p', '--output_sim', type=str)

args = parser.parse_args()

cfg = helper.parse_config(args.config)




def init(cfg):
    nest.ResetKernel()
    nest.set_verbosity("M_FATAL")
    
    seed = [int(time.time() * 10000)]
    print seed
    
    nest.SetKernelStatus({'resolution': cfg["simulation-params"]["resolution"],
                          'print_time': False,
                          'rng_seeds': seed,
                          'local_num_threads': 1,
                          'overwrite_files': True,
                          'syn_update_interval': cfg["simulation-params"]["synapse-update-interval"]})
    
    nest.CopyModel('izhikevich', 'ex_Izhi', {'consistent_integration': False,
                                             'U_m': -0.2 * 65.0,
                                             'b': 0.2,
                                             'c': -65.0,
                                             'a': 0.02,
                                             'd': 8.0,
                                             'tau_minus': 20.})
    
    
    if cfg["network-params"]["plasticity"]["synapse-model"] == 'stdp_izh_synapse':
        nest.CopyModel(cfg["network-params"]["plasticity"]["synapse-model"], "EX", {
            'weight': cfg["network-params"]["plasticity"]['W_init'],
            'Wmax': cfg["network-params"]["plasticity"]['Wmax'],
            'LTP': cfg["network-params"]["plasticity"]['LTP'],
            'LTD': cfg["network-params"]["plasticity"]['LTD'],
            "tau_syn_update_interval": cfg["network-params"]["plasticity"]["tau_syn_update_interval"],
            "constant_additive_value": cfg["network-params"]["plasticity"]["constant_additive_value"],
            "reset_weight_change_after_update": cfg["network-params"]["plasticity"]["reset_weight_change_after_update"]
    
        })
    
    elif cfg["network-params"]["plasticity"]["synapse-model"] == 'stdp_synapse':
        mu_plus = None
        mu_minus = None
        if cfg["network-params"]["plasticity"]["stdp-type"] == 'additive':
            mu_plus = .0
            mu_minus = 0.0
        elif cfg["network-params"]["plasticity"]["stdp-type"] == 'multiplicative':
            mu_plus = 1.0
            mu_minus = 1.0
        else:
            pass
    
        nest.CopyModel(cfg["network-params"]["plasticity"]["synapse-model"], "EX", {
            'weight': cfg["network-params"]["plasticity"]['W_init'],
            'tau_plus': 20.0,
            'lambda': cfg["network-params"]["plasticity"]['lambda'],
            'alpha': cfg["network-params"]["plasticity"]['alpha'],
            'mu_plus': mu_plus,
            'mu_minus': mu_minus,
            'Wmax': cfg["network-params"]["plasticity"]['Wmax']
        })
    
    else:
        nest.CopyModel(cfg["network-params"]["plasticity"]["synapse-model"], "EX", {
            'weight': 6.,
            'consistent_integration': False,
        })



def stim(dt, cfg):
    init(cfg)

    pre = nest.Create("izhikevich")
    post = nest.Create("izhikevich")
    
    nest.Connect(pre, post, 'all_to_all', {'model': 'EX', 'weight': 1., 'delay': 1.})
    
    sg_pre = nest.Create("spike_generator", 1, {"spike_times": [500., 900.]})
    sg_post = nest.Create("spike_generator", 1, {"spike_times": [500. + dt]})
 
    nest.Connect(sg_pre, pre, 'all_to_all', {'model': 'static_synapse', 'weight': 20.})
    nest.Connect(sg_post, post, 'all_to_all', {'model': 'static_synapse', 'weight': 20.})

    nest.Simulate(1010)

    return(nest.GetStatus(nest.GetConnections(pre, post), 'weight')[0] - 1)
    

def simulate(cfg):
    init(cfg)

    pre = nest.Create("izhikevich")
    post = nest.Create("izhikevich")
    
    nest.Connect(pre, post, 'all_to_all', {'model': 'EX', 'weight': 1., 'delay': 1.})
    
    pg_pre = nest.Create("poisson_generator", 1, {"rate": 3.})
    pg_post = nest.Create("poisson_generator", 1, {"rate": 3.})
 
    nest.Connect(pg_pre, pre, 'all_to_all', {'model': 'static_synapse', 'weight': 20.})
    nest.Connect(pg_post, post, 'all_to_all', {'model': 'static_synapse', 'weight': 20.})
    
    ws = []

    for t in range(1000):
        nest.Simulate(1010)

        ws.append(nest.GetStatus(nest.GetConnections(pre, post), 'weight')[0])

    return ws

dts = np.arange(-50, 50, 1.)
dws = []

for dt in dts:
    dws.append(stim(dt, cfg))

with open(args.output, 'w+') as f:
    json.dump({'dt': dts.tolist(), 'dw': dws, 'label': cfg['simulation-params']['data-prefix']}, f)

wss = []
for i in range(100):
    wss.append(simulate(cfg))


with open(args.output_sim, 'w+') as f:
    json.dump({'w': wss, 'label': cfg['simulation-params']['data-prefix']}, f)


