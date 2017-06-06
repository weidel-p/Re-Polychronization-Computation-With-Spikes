import numpy as np
import sys
import pylab as plt

izh_mem = np.loadtxt(sys.argv[1])
nest_mem = np.loadtxt(sys.argv[2])

izh_spikes = np.loadtxt(sys.argv[3])
nest_spikes = np.loadtxt(sys.argv[4])

izh_ssd = np.loadtxt(sys.argv[5])
nest_ssd = np.loadtxt(sys.argv[6])

nest_senders = nest_spikes[:,0]
nest_times = nest_spikes[:,1]
izh_senders = izh_spikes[:,0]
izh_times = izh_spikes[:,1]

izh_mem = izh_mem[1000:]

comparison = [all(izh_mem[i] == nest_mem[i]) for i in range(len(izh_mem))]

print all(comparison)

inv_comp = [not c for c in comparison]

ids_mismatch = np.where(inv_comp)[0]

print "first mismatch at time {t} at neuron {n}".format(t=izh_mem[ids_mismatch[0]][1], n=izh_mem[ids_mismatch[0]][0])

wrong_neurons = np.unique([izh_mem[ids_mismatch[i]][0] for i in range(len(ids_mismatch))])
wrong_neuron = int(wrong_neurons[-1])

def plot_traces(wrong_neuron):
    izh_trace = izh_mem[np.where(izh_mem[:,0] == wrong_neuron)[0], 2]
    nest_trace = nest_mem[np.where(nest_mem[:,0] == wrong_neuron)[0], 2]
    
    izh_cur = izh_mem[np.where(izh_mem[:,0] == wrong_neuron)[0], 4]
    nest_cur = nest_mem[np.where(nest_mem[:,0] == wrong_neuron)[0], 4]
    
    izh_mem_times = izh_mem[np.where(izh_mem[:,0] == wrong_neuron)[0], 1]
    nest_mem_times = nest_mem[np.where(nest_mem[:,0] == wrong_neuron)[0], 1]
    
    nest_spike_train = nest_times[np.where(nest_senders == wrong_neuron)[0]]
    izh_spike_train = izh_times[np.where(izh_senders == wrong_neuron)[0]]
    
    error = np.abs(izh_trace - nest_trace) * -1000000000000000.
    error_cur = np.abs(izh_cur - nest_cur) * -1000000000000000.
    
#    plt.figure()
    plt.plot(izh_trace)
    plt.plot(nest_trace, label=str(wrong_neuron) + " nest")
#    plt.plot(error, label=str(wrong_neuron) + " error")
    plt.plot(error_cur, label=str(wrong_neuron) + " cur")
    plt.legend()


plot_traces(616)
plot_traces(287)

plt.show()



izh_ssd = np.reshape(izh_ssd, [800, 100, 4, 2])
nest_ssd = np.reshape(nest_ssd, [800, 100, 4, 2])

print "weight izh/nest", izh_ssd[0][0][0][0], nest_ssd[0][0][0][0]
print "wdev izh/nest", izh_ssd[0][0][0][1], nest_ssd[0][0][0][1]






