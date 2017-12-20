import numpy as np
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import pylab as plt


def plot_traces(wrong_neuron):
    izh_trace = izh_mem[np.where(izh_mem[:, 0] == wrong_neuron)[0], 2]
    nest_trace = nest_mem[np.where(nest_mem[:, 0] == wrong_neuron)[0], 2]
    #
    # izh_cur = izh_mem[np.where(izh_mem[:,0] == wrong_neuron)[0], 4]
    # nest_cur = nest_mem[np.where(nest_mem[:,0] == wrong_neuron)[0], 4]
    #
    izh_mem_times = izh_mem[np.where(izh_mem[:, 0] == wrong_neuron)[0], 1]
    nest_mem_times = nest_mem[np.where(nest_mem[:, 0] == wrong_neuron)[0], 1]

    nest_spike_train = nest_times[np.where(nest_senders == wrong_neuron)[0]]
    izh_spike_train = izh_times[np.where(izh_senders == wrong_neuron)[0]]

    error = np.abs(izh_trace - nest_trace)

    error *= -1000000000000000.

    # error_cur = np.abs(izh_cur - nest_cur) * -1000000000000000.

    #    plt.figure()
    plt.plot(izh_trace, label=str(wrong_neuron) + "mem pot izh")
    plt.plot(nest_trace, label=str(wrong_neuron) + "mem pot nest")
    plt.plot(error, label=str(wrong_neuron) + "mem error")
    # plt.plot(error_cur, label=str(wrong_neuron) + "cur error")
    plt.legend()
    plt.savefig('{}.pdf'.format(wrong_neuron))
    plt.close()


def get_error(neuron):
    izh_ = izh_mem[np.where(izh_mem[:, 0] == neuron)[0], 2]
    nest_ = nest_mem[np.where(nest_mem[:, 0] == neuron)[0], 2]
    error_ = np.abs(izh_ - nest_)
    return error_


def get_error_u(neuron):
    izh_ = izh_mem[np.where(izh_mem[:, 0] == neuron)[0], 3]
    nest_ = nest_mem[np.where(nest_mem[:, 0] == neuron)[0], 3]
    error_ = np.abs(izh_ - nest_)
    return error_


def get_error_curr(neuron):
    izh_ = izh_mem[np.where(izh_mem[:, 0] == neuron)[0], 4]
    nest_ = nest_mem[np.where(nest_mem[:, 0] == neuron)[0], 4]
    error_ = np.abs(izh_ - nest_)
    return error_


# plot_traces(287)


def spk_plot(senders, times, c, l):
    plt.plot(times, senders, c, label=l, markersize=0.5)


def compare_weight(neuron, time):
    w = abs(izh_ssd[neuron][0][time][0] - nest_ssd[neuron][0][time][0])
    dw = abs(izh_ssd[neuron][0][time][1] - nest_ssd[neuron][0][time][1])
    return [w, dw]



if len(sys.argv) >2:
    izh_mem = np.loadtxt(sys.argv[1])
    nest_mem = np.loadtxt(sys.argv[2])

    izh_mem = izh_mem[:-1000]
    comparison = [all(izh_mem[i] == nest_mem[i]) for i in range(len(izh_mem))]



    inv_comp = [not c for c in comparison]

    ids_mismatch = np.where(inv_comp)[0]

    if len(ids_mismatch > 0):

        wrong_neurons = np.unique([izh_mem[ids_mismatch[i]][0] for i in range(len(ids_mismatch))])
        wrong_neuron = int(wrong_neurons[-1])

if len(sys.argv) >4:

    izh_spikes = np.loadtxt(sys.argv[3])
    nest_spikes = np.loadtxt(sys.argv[4])
    nest_senders = nest_spikes[:, 0]
    nest_times = nest_spikes[:, 1]
    izh_senders = izh_spikes[:, 0]
    izh_times = izh_spikes[:, 1]
    plt.figure()
    spk_plot(nest_senders, nest_times, '.b', 'nest')
    spk_plot(izh_senders, izh_times, '.r', 'izh')
    plt.savefig('plot.png')
    plt.close()
if len(sys.argv) >6:

    izh_ssd = np.loadtxt(sys.argv[5])
    nest_ssd = np.loadtxt(sys.argv[6])

    izh_ssd = np.reshape(izh_ssd, [800, 100, 50, 2])  # Format: neuron, synapse, time in sec, [w, w_dev]
    nest_ssd = np.reshape(nest_ssd, [800, 100, 50, 2])


    ws = []
    dws = []
    for n in range(800):
        for time in range(5):
            w, dw = compare_weight(n,time)
            ws.append(w)
            dws.append(dw)








