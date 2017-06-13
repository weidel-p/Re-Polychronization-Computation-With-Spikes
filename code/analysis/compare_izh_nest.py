import numpy as np
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
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

if len(ids_mismatch > 0):
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
    plt.plot(izh_trace, label=str(wrong_neuron) + "mem pot izh")
    plt.plot(nest_trace, label=str(wrong_neuron) + "mem pot nest")
    plt.plot(error, label=str(wrong_neuron) + "mem error")
    plt.plot(error_cur, label=str(wrong_neuron) + "cur error")
    plt.legend()

def get_error(neuron):
    if neuron % 100 == 0:
        print neuron
    izh_ = izh_mem[np.where(izh_mem[:,0] == neuron)[0], 2]
    nest_ = nest_mem[np.where(nest_mem[:,0] == neuron)[0], 2]
    error_ = np.abs(izh_ - nest_)
    return error_
 
def get_error_u(neuron):
    if neuron % 100 == 0:
        print neuron
    izh_ = izh_mem[np.where(izh_mem[:,0] == neuron)[0], 3]
    nest_ = nest_mem[np.where(nest_mem[:,0] == neuron)[0], 3]
    error_ = np.abs(izh_ - nest_) 
    return error_
       

def get_error_curr(neuron):
    if neuron % 100 == 0:
        print neuron
    izh_ = izh_mem[np.where(izh_mem[:,0] == neuron)[0], 4]
    nest_ = nest_mem[np.where(nest_mem[:,0] == neuron)[0], 4]
    error_ = np.abs(izh_ - nest_) 
    return error_
    

plot_traces(616)
#plot_traces(287)


def spk_plot(senders, times, c, l):
    plt.plot(times, senders, c, label=l)

plt.figure()
spk_plot(nest_senders-1, nest_times, '.b', 'nest')
spk_plot(izh_senders, izh_times, '.r', 'izh')

izh_ssd = np.reshape(izh_ssd, [800, 100, 101, 2]) # Format: neuron, synapse, time in sec, [w, w_dev]
nest_ssd = np.reshape(nest_ssd, [800, 100, 101, 2])

def compare_weight(neuron):
    if neuron % 100 == 0:
        print neuron
    w = abs(izh_ssd[neuron][0][100][0] - nest_ssd[neuron][0][100][0])
    dw = abs(izh_ssd[neuron][0][100][1] - nest_ssd[neuron][0][100][1])
    return [w, dw]


ws = []
dws = []
for n in range(800):
    w, dw = compare_weight(n)
    ws.append(w)
    dws.append(dw)

print "max error w / dw", max(ws), max(dws)

mem_error = []
curr_error = []
u_error =[]
for n in range(1000):
    mem_error.append(get_error(n+1))
    curr_error.append(get_error_curr(n+1))
    u_error.append(get_error_u(n+1))

print "max mem error", max([max(e)for e in mem_error]) 
print "max curr error", max([max(e)for e in curr_error]) 
print "max u error", max([max(e)for e in u_error]) 
    
#print "max error mem / curr / u at ", np.argmax(mem_error), np.argmax(curr_error), np.argmax(u_error)





plt.show()


