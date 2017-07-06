import os,glob,sys
sys.path.insert(0, 'code/NEST_model/') #ugly but not sure how to otherwise handle this

import socket
if "cluster" in socket.gethostname():
    shell.prefix('module load autotools;module load pystuff_new; module load mpi/openmpi/1.10.0;')
    NUM_THREADS=8
else:
    NUM_THREADS=3

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

PLOT_FILES = ['plot_8.png','plot_7.png','dynamics.png']
MAN_DIR='manuscript/8538120cqhctwxyjvvn'
FIG_DIR='figures'
LOG_DIR='logs'
CONFIG_DIR=os.path.join(NEST_CODE_DIR,'experiments')

CONFIG_FILES=[file[:-5] for file in os.listdir(CONFIG_DIR) ]
#repetition is used to set seed to get statistics for the experiemnts
NUM_REP=range(5)
include: "Izhikevic.rules"
include: "nest.rules"

rule all:
    input:
        #test_plot_mem='figures/test_bitwise_reproduction_mem.pdf',
        #test_plot_spk='figures/test_bitwise_reproduction_spk.pdf',
        #test_plot_5=expand('figures/{experiment}/{rep}/dynamic_measures.png',experiment=CONFIG_FILES,rep=NUM_REP),
        #weight_distributions=expand('{folder}/{experiment}/{rep}/weight_distribution.pdf',folder=FIG_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        #delay_distributions=expand('{folder}/{experiment}/{rep}/delay_distribution.pdf',folder=FIG_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        nest_groups=expand("{folder}/{experiment}/{rep}/groups.json",folder=NEST_DATA_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        nest_connectivity=expand("{folder}/{experiment}/{rep}/connectivity.json",folder=NEST_DATA_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        nest_spikes=expand("{folder}/{experiment}/{rep}/spikes-1001.gdf",folder=NEST_DATA_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        nest_membrane=expand("{folder}/{experiment}/{rep}/membrane_potential-1002.dat",folder=NEST_DATA_DIR,experiment=CONFIG_FILES,rep=NUM_REP),
        plot_combined=expand('{folder}/{experiment}/{experiment}_combined_groups.png',folder=FIG_DIR,experiment=CONFIG_FILES),
        plt_bitwise=expand('figures/bitwise_reproduction_{rep}.png',rep=NUM_REP),
        plt_naive=expand('figures/bitwise_naive_{rep}.png',rep=NUM_REP),
        plt_statistical=expand('figures/bitwise_statistical_{rep}.png',rep=NUM_REP),

        plot_files=expand('{folder}/{experiment}/{rep}/{plot}',folder=FIG_DIR,experiment=CONFIG_FILES,rep=NUM_REP,plot=PLOT_FILES),
        original_groups=expand("{folder}/bitwise_reproduction/{rep}/groups.json",folder=IZHI_DATA_DIR,rep=NUM_REP),
        original_weights=expand("{folder}/bitwise_reproduction/{rep}/connectivity.json",folder=IZHI_DATA_DIR,rep=NUM_REP),






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

rule find_groups:
    output:
        "{folder}/{experiment}/{rep}/groups.json"
    input:
        connectivity="{folder}/{experiment}/{rep}/connectivity.json",
        program=rules.compile_find_polychronous_groups.output,
    log: 'logs/find_groups_{experiment}_{rep}.log'
    run:
        shell('{input.program} {input.connectivity} {output} &>{log}')
rule plot_test_statistical_reproduction:
    input:
        stat_con=expand('{folder}/statistical_equivalence/{{rep}}/connectivity.json',folder=NEST_DATA_DIR),
        bit_con=expand('{folder}/bitwise_reproduction/{{rep}}/connectivity.json',folder=NEST_DATA_DIR),
        stat_spk=expand('{folder}/statistical_equivalence/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),
        bit_spk=expand('{folder}/bitwise_reproduction/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),

    output:
        'figures/bitwise_statistical_{rep}.png',
    shell:
        'python {ANA_DIR}/plot_statistical_reproduction.py -bs {{input.bit_spk}} -ss {{input.stat_spk}} -bw {{input.bit_con}} -sw {{input.stat_con}} -fn {{output}}'.format(ANA_DIR=ANA_DIR,fig_dir=FIG_DIR)

rule plot_test_naive_reproduction:
    input:
        naive_con=expand('{folder}/naive_reproduction/{{rep}}/connectivity.json',folder=NEST_DATA_DIR),
        bit_con=expand('{folder}/bitwise_reproduction/{{rep}}/connectivity.json',folder=NEST_DATA_DIR),
        naive_spk=expand('{folder}/naive_reproduction/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),
        bit_spk=expand('{folder}/bitwise_reproduction/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),

    output:
        'figures/bitwise_naive_{rep}.png',
    shell:
        'python {ANA_DIR}/plot_bitwise_naive.py -bs {{input.bit_spk}} -ns {{input.naive_spk}} -bw {{input.bit_con}} -nw {{input.naive_con}} -fn {{output}}'.format(ANA_DIR=ANA_DIR,fig_dir=FIG_DIR)


rule plot_test_bitwise_reproduction:
    input:
        original_spk=expand('{folder}/bitwise_reproduction/{{rep}}/spikes.dat',folder=IZHI_DATA_DIR),
        nest_mem=expand('{folder}/bitwise_reproduction/{{rep}}/membrane_potential-1002.dat',folder=NEST_DATA_DIR),
        nest_spk=expand('{folder}/bitwise_reproduction/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),
    output:
        'figures/bitwise_reproduction_{rep}.png',
    shell:
        'python {ANA_DIR}/plot_bitwise_reproduction.py -bs {{input.nest_spk}} -os {{input.original_spk}} -bmem {{input.nest_mem}} -fn {{output}}'.format(ANA_DIR=ANA_DIR,fig_dir=FIG_DIR)

rule plot_groups:
    output:
        plot_7=expand('{folder}/{{experiment}}/{{rep}}/plot_7.png',folder=FIG_DIR),
        plot_8=expand('{folder}/{{experiment}}/{{rep}}/plot_8.png',folder=FIG_DIR),

    input:
        groups=expand('{folder}/{{experiment}}/{{rep}}/groups.json',folder=NEST_DATA_DIR),
    priority: 1
    run:
        shell("""
        python code/analysis/plot_group_statistics.py \
        --groupfile {input.groups}\
        --outfolder figures/{wildcards.experiment}/{wildcards.rep}\
        """)
rule plot_combined_groups:
    output:
        plot_8=expand('{folder}/{{experiment}}/{{experiment}}_combined_groups.png',folder=FIG_DIR),

    input:
        groups=expand('{folder}/{{experiment}}/{rep}/groups.json',folder=NEST_DATA_DIR,rep=NUM_REP),
    priority: 1
    run:
        shell("""
        python code/analysis/plot_combined_group_statistics.py \
        -gl {input.groups}\
        -fn {output.plot_8}\
        """)


rule plot_dynamics:
    output:
        file=expand('{folder}/{{experiment}}/{{rep}}/dynamics.png',folder=FIG_DIR),
    input:
        connectivity=expand('{folder}/{{experiment}}/{{rep}}/connectivity.json',folder=NEST_DATA_DIR),
        spikes=expand('{folder}/{{experiment}}/{{rep}}/spikes-1001.gdf',folder=NEST_DATA_DIR),
    priority: 2
    run:
        shell("""
        python code/analysis/plot_dynamics.py \
        --spikefile {input.spikes}\
        --weightfile {input.connectivity}\
        --outfolder figures/{wildcards.experiment}/{wildcards.rep}\
        --filename dynamics.png
        """)