import os,glob,sys
sys.path.insert(0, 'code/model/') #ugly but not sure how to otherwise handle this
import params
WEIGHT_SAMPLES = ['weights_{:02d}.dat'.format(i) for i in range(params.N_measure)]        #define the weights files output to model.py and input to the cpp code
GROUP_SAMPLES = ['target_{:02d}.txt'.format(i) for i in range(params.N_measure)]   # define files output of cpp code and input to example_plots.py



rule make_plots:
    output:
        'figures/plot_5'
    input:
        expand("data/{file}",file=GROUP_SAMPLES)
    shell:
        'cd code/model/;python example_plots.py'

rule find_groups:
    output:
        expand("data/{file}",file=GROUP_SAMPLES)
    input:
        expand("data/{file}",file=WEIGHT_SAMPLES),
        'code/analysis/find_polychronous_groups'
    run:
        for job in zip(WEIGHT_SAMPLES,GROUP_SAMPLES):
            print("./find_polychronous_groups ../../data/{} ../../data/{}".format(job[0],job[1]))
            shell("cd code/analysis;./find_polychronous_groups ../../data/{} ../../data/{}".format(job[0],job[1]))

rule compile_cpp:
	output:
	    'code/analysis/find_polychronous_groups'
	input:
	    'code/analysis/find_polychronous_groups.cpp'
	shell:
	    'g++ -o code/analysis/find_polychronous_groups code/analysis/find_polychronous_groups.cpp'

rule run_model:
    output:
        expand("data/{file}.dat",file=WEIGHT_SAMPLES)
    input:
        'code/model/model.py'
    shell:
        'cd code/model/;python model.py'