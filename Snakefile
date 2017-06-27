import os,glob,sys
sys.path.insert(0, 'code/NEST_model/') #ugly but not sure how to otherwise handle this

import socket
if "cluster" in socket.gethostname():
    shell.prefix('module load autotools;module load pystuff_new; module load mpi/openmpi/1.10.0;')


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

PLOT_FILES = ['plot_8.pdf','plot_5.pdf','plot_7.pdf']
MAN_DIR='manuscript/8538120cqhctwxyjvvn'
FIG_DIR='figures'
LOG_DIR='logs'
CONFIG_DIR=os.path.join(NEST_CODE_DIR,'experiments')

CONFIG_FILES=[file[:-5] for file in os.listdir(CONFIG_DIR)]
#repetition is used to set seed to get statistics for the experiemnts
repetitions=5

include: "Izhikevic.rules"
include: "nest.rules"

rule all:
    input:
        test_plot_mem='figures/test_bitwise_reproduction_mem.pdf',
        test_plot_spk='figures/test_bitwise_reproduction_spk.pdf',
        test_plot_5=expand('figures/{experiment}_plot_5.pdf',experiment=CONFIG_FILES),
        weight_distributions=expand('{folder}/{experiment}_weight_distribution.pdf',folder=FIG_DIR,experiment=CONFIG_FILES),
        delay_distributions=expand('{folder}/{experiment}_delay_distribution.pdf',folder=FIG_DIR,experiment=CONFIG_FILES),

        original_groups=expand("{folder}/reformat_groups.json",folder=IZHI_DATA_DIR),
        original_weights=expand("{folder}/reformat_connectivity.json",folder=IZHI_DATA_DIR),






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
        "{folder}/{pre}_groups.json"
    input:
        connectivity="{folder}/{pre}_connectivity.json",
        program=rules.compile_find_polychronous_groups.output,
    log: 'logs/find_groups_{pre}.log'
    run:
        shell('{input.program} {input.connectivity} {output} &>{log}')


rule test_weights_and_delay:
    input:
        nest=expand('{folder}/{{experiment}}_connectivity.json',folder=[NEST_DATA_DIR]),
    output:
        weight=expand('{folder}/{{experiment}}_weight_distribution.pdf',folder=FIG_DIR),
        delay=expand('{folder}/{{experiment}}_delay_distribution.pdf',folder=FIG_DIR)
    priority:1

    shell:
        'python {ANA_DIR}/weight_and_delay_distribution.py -c {{input}} -wo {{output.weight}} -do {{output.delay}}'.format(ANA_DIR=ANA_DIR)

rule test_bitwise_reproduction:
    input:
        original_mem=expand('{folder}/bitwise_reproduction_vu.dat',folder=IZHI_DATA_DIR),
        original_spk=expand('{folder}/bitwise_reproduction_spikes.dat',folder=IZHI_DATA_DIR),
        nest_mem=expand('{folder}/bitwise_reproduction-1002-0.dat',folder=NEST_DATA_DIR),
        nest_spk=expand('{folder}/bitwise_reproduction_spikes-1001-0.gdf',folder=NEST_DATA_DIR),
    output:
        'figures/test_bitwise_reproduction_spk.pdf',
        'figures/test_bitwise_reproduction_mem.pdf',
    shell:
        'python {ANA_DIR}/test_bitwise_reproduction.py -i {{input.original_mem}} -n {{input.nest_mem}} -si {{input.original_spk}} -sn {{input.nest_spk}} -o {fig_dir} '.format(ANA_DIR=ANA_DIR,fig_dir=FIG_DIR)

ruleorder: make_plots_1 > make_plots_2

rule make_plots_1:
    output:
        '{folder}/{{experiment}}_plot_5.pdf'.format(folder=FIG_DIR)
    input:
        connectivity='{folder}/{{experiment}}_connectivity.json'.format(folder=NEST_DATA_DIR),
        groups='{folder}/{{experiment}}_groups.json'.format(folder=NEST_DATA_DIR),
        spikes='{folder}/{{experiment}}_spikes-1001-0.gdf'.format(folder=NEST_DATA_DIR),
    priority: 1
    run:
        shell("""
        python code/analysis/make_plots.py \
        --groupfile data/NEST_model/{wildcards.experiment}_groups.json \
        --spikefile data/NEST_model/{wildcards.experiment}_spikes-1001-0.gdf\
        --weightfile data/NEST_model/{wildcards.experiment}_connectivity.json\
        --outfolder figures\
        --prefix {wildcards.experiment}
        """)

rule make_plots_2:
    output:
        '{folder}/{{experiment}}_plot_5.pdf'.format(folder=FIG_DIR)
    input:
        connectivity='{folder}/{{experiment}}_connectivity.json'.format(folder=NEST_DATA_DIR),
        groups='{folder}/{{experiment}}_groups.json'.format(folder=NEST_DATA_DIR),
        spikes='{folder}/{{experiment}}_spikes-1001-0.gdf'.format(folder=NEST_DATA_DIR),
    priority:1
    run:
        shell("""
        python code/analysis/make_plots.py \
        --groupfile {input.groups} \
        --spikefile {input.spikes}\
        --weightfile {input.connectivity}\
        --outfolder figures\
        --prefix {wildcards.experiment}
        """)

"""



rule create_pdf:
    output:
        expand('{folder}/main.pdf',folder=MAN_FOLDER)
    input:
        'manuscript/8538120cqhctwxyjvvn/main.tex',
        expand("{folder}/{fig_folder}/{file}",folder=MAN_FOLDER,fig_folder=FIG_FOLDER,file=PLOT_FILES)
    shell:
        "cd {folder};pdflatex main.tex".format(folder=MAN_FOLDER)


rule move_to_manuscript:
    output:
         expand("{folder}/figures/{file}",folder=MAN_FOLDER,file=PLOT_FILES)
    input:
         expand("figures/{file}",file=PLOT_FILES)
    run:
        for move in zip(input,output):
            shell("cp {} {}".format(move[0],move[1]))


"""
