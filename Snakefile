import os,glob,sys
import numpy as np

sys.path.insert(0, 'code/NEST_model/') #ugly but not sure how to otherwise handle this

import socket
if "cluster" in socket.gethostname():
    shell.prefix('module load autotools; module load mpi/openmpi/1.10.0;source activate poly-python3;')
    NUM_THREADS=1
else:
    NUM_THREADS=1

#Define folders:
CUR_DIR=os.getcwd()
CODE_DIR='code'
DATA_DIR='data'

nest_prefix='NEST_model'
izhi_prefix='original_model'

NEST_CODE_DIR=os.path.join(CODE_DIR,nest_prefix)
NEST_DATA_DIR=os.path.join(DATA_DIR,nest_prefix)

IZHI_CODE_DIR=os.path.join(CODE_DIR,izhi_prefix)
IZHI_DATA_DIR=os.path.join(DATA_DIR,izhi_prefix)

#compile poly_spnet into a folder because it outputs into ../
IZHI_EXEC_DIR=os.path.join(IZHI_CODE_DIR,'exec')
ANA_DIR=os.path.join(CODE_DIR,'analysis')
NEST_SRC_DIR=os.path.join(CUR_DIR,os.path.join(
            CODE_DIR,'nest/nest-simulator'))

PLOT_FILES = ['dynamic_measures.png','plot_8.png']
MAN_DIR='manuscript/8538120cqhctwxyjvvn'
FIG_DIR='figures'
LOG_DIR='logs'
CONFIG_DIR=os.path.join(NEST_CODE_DIR,'experiments')

#CONFIG_FILES=[file[:-5] for file in os.listdir(CONFIG_DIR) if ('bitwise' in file) or ('statistical' in file)]
CONFIG_FILES=[file[:-5] for file in os.listdir(CONFIG_DIR) if ('polychrony' not in file) ]

repro_CONFIG_FILES=[file[:-5] for file in os.listdir(CONFIG_DIR) if ('reproduction' in file) and ('polychrony' not in file)]
repro_CONFIG_FILES=[file.split('_')[0] for file in repro_CONFIG_FILES]
#repetition is used to set seed to get statistics for the experiemnts
low_NUM_REP=range(1)
low_CONFIG_FILES=[file[:-5] for file in os.listdir(CONFIG_DIR) if ('reproduction' not in file) ]

high_NUM_REP=range(20)
high_CONFIG_FILES=[file[:-5] for file in os.listdir(CONFIG_DIR) if ('reproduction' in file) and ('polychrony' not in file) ]
NUM_REP=high_NUM_REP

RANGE_PROB_EX_EX = np.round(np.linspace(0, 1, 20), 2)

include: "Izhikevic.rules"
include: "nest.rules"

rule all:
    input:
        rand_conn = expand("data/NEST_model/bitwise_reproduction/0/groups_random_conn_{prob}.json", prob=RANGE_PROB_EX_EX)
        #polytest_full_data=expand("{folder}/{experiment}/{rep}/groups.json",
        #                    folder=NEST_DATA_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        #polytest_data_full_nest=expand("{folder}/{experiment}/{rep}/groups_nest.json",
        #                    folder=NEST_DATA_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        #plt_bimodal_gamma=expand('figures/{experiment}/{experiment}_bimodalgamma_groups.eps',experiment=CONFIG_FILES),
        #plt_bimodal_gamma_nest=expand('figures/{experiment}/{experiment}_bimodalgamma_groups_nest.eps',experiment=CONFIG_FILES),



        #nest_groups_repro=expand("{folder}/{experiment}/{rep}/groups.json",
        #                    folder=NEST_DATA_DIR,experiment=high_CONFIG_FILES,rep=high_NUM_REP),

        #nest_groups_repro_nest=expand("{folder}/{experiment}/{rep}/groups_nest.json",
        #                    folder=NEST_DATA_DIR,experiment=high_CONFIG_FILES,rep=high_NUM_REP),

        #nest_connectivity_repro=expand("{folder}/{experiment}/{rep}/connectivity.json",
        #                            folder=NEST_DATA_DIR,experiment=high_CONFIG_FILES,rep=high_NUM_REP),

        #plt_statistical=expand('figures/bitwise_{experiment}_{rep}.eps',
        #                    experiment=repro_CONFIG_FILES,rep=low_NUM_REP),


        #plt_bitwise=expand('figures/bitwise_reproduction_{rep}.eps',rep=low_NUM_REP),




        #nest_groups_exp=expand("{folder}/{experiment}/{rep}/groups.json",
        #                    folder=NEST_DATA_DIR,experiment=low_CONFIG_FILES,rep=low_NUM_REP),
        #nest_connectivity_exp=expand("{folder}/{experiment}/{rep}/connectivity.json",
        #                            folder=NEST_DATA_DIR,experiment=low_CONFIG_FILES,rep=low_NUM_REP),


        #nest_spikes=expand("{folder}/{experiment}/{rep}/spikes-1001.gdf",
        #                    folder=NEST_DATA_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        #nest_membrane=expand("{folder}/{experiment}/{rep}/membrane_potential-1002.dat",
        #                    folder=NEST_DATA_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        #plot_combined=expand('{folder}/{experiment}/{experiment}_combined_groups.png',
        #                        folder=FIG_DIR,experiment=CONFIG_FILES),
      
        #plot_files=expand('{folder}/{experiment}/{rep}/{plot}',
        #                    folder=FIG_DIR,experiment=low_CONFIG_FILES,rep=low_NUM_REP,plot=PLOT_FILES),


        #original_groups=expand("{folder}/bitwise_reproduction/{rep}/groups.json",
        #                        folder=IZHI_DATA_DIR,rep=NUM_REP),
        #original_weights=expand("{folder}/bitwise_reproduction/{rep}/connectivity.json",
        #                    folder=IZHI_DATA_DIR,rep=NUM_REP),
        #original_code=expand("{folder}/{rep}/poly_spnet_bitwise_reproduction",
        #                    folder=IZHI_EXEC_DIR,rep=NUM_REP),




rule clean:
    shell:
        """
        rm -rf {data}/*
        rm -rf {code}/*.dat
        rm -rf {exec}/*
        rm -rf {fig}/*
        rm -rf {logs}/*
        """.format(exec=IZHI_EXEC_DIR,fig=FIG_DIR,data=DATA_DIR,code=IZHI_CODE_DIR,logs=LOG_DIR)

rule compile_find_polychronous_groups:
	output:
	    expand('{folder}/find_polychronous_groups',folder=ANA_DIR)
	input:
	    expand('{folder}/find_polychronous_groups.cpp',folder=ANA_DIR)
	shell:
	    'g++ -o {output} {input} -ljsoncpp'


rule compile_find_polychronous_groups_random:
	output:
	    expand('{folder}/find_polychronous_groups_random_weight_dist',folder=ANA_DIR)
	input:
	    expand('{folder}/find_polychronous_groups_random_weight_dist.cpp',folder=ANA_DIR)
	shell:
	    'g++ -o {output} {input} -ljsoncpp'


rule find_groups:
    output:
        "{folder}/{experiment}/{rep}/groups.json"
    input:
        connectivity="{folder}/{experiment}/{rep}/connectivity.json",
        program=rules.compile_find_polychronous_groups.output,
    log: 'logs/find_groups_{experiment}_{rep}.log'
    shell:
        '{input.program} {input.connectivity} {output} &>{log}'

rule find_groups_random:
    output:
        "data/NEST_model/bitwise_reproduction/0/groups_random_conn_{prob}.json",
    input:
        connectivity="data/NEST_model/bitwise_reproduction/0/connectivity.json",
        program=rules.compile_find_polychronous_groups_random.output,
#    log: 'logs/find_groups_{experiment}_{rep}.log'
    shell:
        '{input.program} {input.connectivity} {output} {wildcards.prob} 1.0 ' #&>{log}'


rule plot_test_statistical_reproduction:
    input:
        stat_con=expand('{folder}/{{experiment}}_reproduction/{{rep}}/connectivity.json',folder=NEST_DATA_DIR),
        bit_con=expand('{folder}/bitwise_reproduction/{{rep}}/connectivity.json',folder=NEST_DATA_DIR),
        stat_spk=expand('{folder}/{{experiment}}_reproduction/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),
        bit_spk=expand('{folder}/bitwise_reproduction/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),
    output:
        'figures/bitwise_{experiment}_{rep}.{ext,(eps|png)}',
    priority: 9
    shell:
        'python3 {ANA_DIR}/plot_statistical_reproduction.py -bs {{input.bit_spk}} -ss {{input.stat_spk}} -bw {{input.bit_con}} -sw {{input.stat_con}} -fn {{output}}'.format(ANA_DIR=ANA_DIR,fig_dir=FIG_DIR)

rule plot_test_bitwise_reproduction:
    input:
        original_spk=expand('{folder}/bitwise_reproduction/{{rep}}/spikes.dat',folder=IZHI_DATA_DIR),
        nest_mem=expand('{folder}/bitwise_reproduction/{{rep}}/membrane_potential-1002.dat',folder=NEST_DATA_DIR),
        nest_spk=expand('{folder}/bitwise_reproduction/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),
    output:
        'figures/bitwise_reproduction_{rep}.{ext,(eps|png)}',
    priority: 10
    shell:
        'python3 {ANA_DIR}/plot_bitwise_reproduction.py -bs {{input.nest_spk}} -os {{input.original_spk}} -bmem {{input.nest_mem}} -fn {{output}}'.format(ANA_DIR=ANA_DIR,fig_dir=FIG_DIR)

rule plot_groups:
    output:
        plot_7=expand('{folder}/{{experiment}}/{{rep}}/plot_7.{{ext,(eps|png)}}',folder=FIG_DIR),
        plot_8=expand('{folder}/{{experiment}}/{{rep}}/plot_8.{{ext,(eps|png)}}',folder=FIG_DIR),

    input:
        groups=expand('{folder}/{{experiment}}/{{rep}}/groups.json',folder=NEST_DATA_DIR),
    priority: 2
    run:
        shell("""
        python3 code/analysis/plot_group_statistics.py \
        --groupfile {input.groups}\
        --outfolder figures/{wildcards.experiment}/{wildcards.rep}\
        """)

rule plot_combined_groups:
    output:
        plot_8=expand('{folder}/{{experiment}}/{{experiment}}_combined_groups.{{ext,(eps|png)}}',folder=FIG_DIR),

    input:
        groups=expand('{folder}/{{experiment}}/{rep}/groups.json',folder=NEST_DATA_DIR,rep=NUM_REP),
    priority: 2
    run:
        shell("""
        python3 code/analysis/plot_combined_group_statistics.py \
        -gl {input.groups}\
        -fn {output.plot_8}\
        """)

rule plot_bimodal_gamma:
    output:
        weight=expand('{folder}/{{experiment}}/{{experiment}}_bimodalgamma_weight_delay.{{ext,(eps|png)}}',folder=FIG_DIR),
        groups=expand('{folder}/{{experiment}}/{{experiment}}_bimodalgamma_groups.{{ext,(eps|png)}}',folder=FIG_DIR),

    input:
        connectivity=expand('{folder}/{{experiment}}/{rep}/connectivity.json',folder=NEST_DATA_DIR,rep=NUM_REP),
        spikes=expand('{folder}/{{experiment}}/{rep}/spikes-1001.gdf',folder=NEST_DATA_DIR,rep=NUM_REP),
        groups=expand('{folder}/{{experiment}}/{rep}/groups.json',folder=NEST_DATA_DIR,rep=NUM_REP),

    priority: 2
    run:
        shell("""
        python3 code/analysis/plot_bimodal_gamma.py \
        -cl {input.connectivity}\
        -sl {input.spikes}\
        -gl {input.groups}\
        --group_plot {output.groups}\
        --gamma_plot {output.weight}\

        """)

rule plot_bimodal_gamma_nest:
    output:
        weight=expand('{folder}/{{experiment}}/{{experiment}}_bimodalgamma_weight_delay.{{ext,(eps|png)}}',folder=FIG_DIR),
        groups=expand('{folder}/{{experiment}}/{{experiment}}_bimodalgamma_groups_nest.{{ext,(eps|png)}}',folder=FIG_DIR),

    input:
        connectivity=expand('{folder}/{{experiment}}/{rep}/connectivity.json',folder=NEST_DATA_DIR,rep=NUM_REP),
        spikes=expand('{folder}/{{experiment}}/{rep}/spikes-1001.gdf',folder=NEST_DATA_DIR,rep=NUM_REP),
        groups=expand('{folder}/{{experiment}}/{rep}/groups_nest.json',folder=NEST_DATA_DIR,rep=NUM_REP),

    priority: 2
    run:
        shell("""
        python3 code/analysis/plot_bimodal_gamma.py \
        -cl {input.connectivity}\
        -sl {input.spikes}\
        -gl {input.groups}\
        --group_plot {output.groups}\
        --gamma_plot {output.weight}\

        """)

rule test_weights_and_delay:
    input:
        nest=expand('{folder}/{{experiment}}/{{rep}}/connectivity.json',folder=NEST_DATA_DIR),
    output:
        weight=expand('{folder}/{{experiment}}/{{rep}}/weight_distribution.{{ext,(eps|png)}}',folder=FIG_DIR),
    priority: 10
    shell:
        'python3 {ANA_DIR}/weight_and_delay_distribution.py -c {{input.nest}} -o {{output.weight}} '.format(ANA_DIR=ANA_DIR)

rule plot_dynamics:
    output:
        file=expand('{folder}/{{experiment}}/{{rep}}/dynamic_measures.{{ext,(eps|png)}}',folder=FIG_DIR),
    input:
        connectivity=expand('{folder}/{{experiment}}/{{rep}}/connectivity.json',folder=NEST_DATA_DIR),
        spikes=expand('{folder}/{{experiment}}/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),
    priority: 2
    run:
        shell("""
        python3 code/analysis/plot_dynamics.py \
        --spikefile {input.spikes}\
        --weightfile {input.connectivity}\
        --filename {output}
        """)
