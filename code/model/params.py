import numpy as np

N=1000
N_inh=200
N_ex=800
N_syn=100
delays=np.random.randint(1,20,N_ex)
weight=10
tau_plus=20
tau_minus=20
Aplus=0.1
Aminus=0.12
T_measure=18.0 * 60 * 60 * 1000
N_measure=18
dt=1.0

