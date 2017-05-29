import os,glob,sys
sys.path.insert(0, 'code/NEST_model/') #ugly but not sure how to otherwise handle this
from params import *

#Define folders:
CUR_DIR=os.getcwd()
CODE_DIR=os.path.join(CUR_DIR,'code')
DATA_DIR=os.path.join(CUR_DIR,'data')

nest_prefix='NEST_model'
izhi_prefix='original_model'
NEST_CODE_DIR=os.path.join(CODE_DIR,nest_prefix)
NEST_DATA_DIR=os.path.join(DATA_DIR,nest_prefix)

IZHI_CODE_DIR=os.path.join(CODE_DIR,izhi_prefix)
IZHI_DATA_DIR=os.path.join(DATA_DIR,izhi_prefix)

#compile poly_spnet into a folder because it outputs into ../
IZHI_EXEC_DIR=os.path.join(IZHI_CODE_DIR,'exec')
ANA_DIR=os.path.join(CODE_DIR,'analysis')
NEST_SRC_DIR=os.path.join(
            CODE_DIR,'nest/nest-simulator')


PREFIX = ['NEST']
WEIGHT_SAMPLES = ['all_{:02d}.json'.format(i) for i in range(1,N_measure+1)]        #define the weights files output to model.py and input to the cpp code
SPIKE_SAMPLES = ['spikes-{:02d}-0.gdf'.format(1002) for i in range(1,N_measure+1)]        #define the spike files
GROUP_SAMPLES = ['groups_{:02d}.json'.format(i) for i in range(1,N_measure+1)]   # define files output of cpp code and input to example_plots.py
PLOT_FILES = ['plot_8.pdf','plot_5.pdf','plot_7.pdf']
MAN_DIR='manuscript/8538120cqhctwxyjvvn'
FIG_DIR='figures'

include: "Izhikevic.rules"
include: "nest.rules"


rule all:
    input:
        test_plot_weight='figures/weight_distribution.pdf',
        test_plot_delay='figures/delay_distribution.pdf',
        weight='figures/single_stim_weight_distribution.pdf',
        delay='figures/single_stim_delay_distribution.pdf',

        test_membrane='figures/membrane_potential_comparison.pdf',
        test_rasta='figures/spikes_comparison.pdf',

        original_groups=expand("{folder}/reformat_groups_01.json",folder=IZHI_DATA_DIR),
        original_weights=expand("{folder}/reformat_all_01.json",folder=IZHI_DATA_DIR),
        original_repro=expand("{folder}/reformat_single_stim_all_01.json",folder=IZHI_DATA_DIR),
        nest_groups=expand("{folder}/{pre}_{file}",folder=NEST_DATA_DIR,file=GROUP_SAMPLES,pre=PREFIX),
        nest_weight=expand("{folder}/{pre}_{file}",folder=NEST_DATA_DIR,file=WEIGHT_SAMPLES,pre=PREFIX),




rule clean:
    shell:
        "rm $(snakemake --summary | tail -n+2 | cut -f1)"


rule compile_find_polychronous_groups:
	output:
	    expand('{folder}/find_polychronous_groups',folder=ANA_DIR)
	input:
	    expand('{folder}/find_polychronous_groups.cpp',folder=ANA_DIR)
	shell:
	    'g++ -o {output} {input} -ljsoncpp'

rule find_groups:
    output:
        "{folder}/{pre}_groups_{file}.json"
    input:
        "{folder}/{pre}_all_{file}.json",
        program=rules.compile_find_polychronous_groups.output,

    run:
        shell('{input.program} {input} {output}')

rule test_single_neuron_dynamics:
    input:
        original_weight=rules.original_single_neuron_test.output.mem,
        original_spk=rules.original_single_neuron_test.output.spk,
        nest_weight=rules.nest_single_neuron_test.output.mem,
        nest_spk=rules.nest_single_neuron_test.output.spk

    output:
        'figures/membrane_potential_comparison.pdf',
        'figures/spikes_comparison.pdf',

    shell:
        'python {ANA_DIR}/single_neuron_dynamics_plot.py -i {{input.original_weight}} -n {{input.nest_weight}} -si {{input.original_spk}} -sn {{input.nest_spk}} -o {fig_dir} '.format(ANA_DIR=ANA_DIR,fig_dir=FIG_DIR)

rule test_weights_and_delay:
    input:
        nest=expand('{folder}/NEST_{{stim,.*}}all_01.json',folder=NEST_DATA_DIR),
        original=expand('{folder}/reformat_{{stim,.*}}all_01.json',folder=IZHI_DATA_DIR)
    output:
        weight='figures/{stim,.*}weight_distribution.pdf',
        delay='figures/{stim,.*}delay_distribution.pdf'

    shell:
        'python {ANA_DIR}/weight_and_delay_distribution.py -i {{input.original}} -n {{input.nest}} -wo {{output.weight}} -do {{output.delay}}'.format(ANA_DIR=ANA_DIR)


"""
rule make_plots:
    output:
        expand("{folder}/{pre}_{file}",folder=FIG_DIR,file=PLOT_FILES,pre=PREFIX)
    input:
        nest_weights=rules.run_model.output.weights,
        nest_groups=rules.find_groups.output.nest,
        nest_spikes=rules.run_model.output.spikes,
        original_weights=expand("{folder}/{file}",folder=IZHI_DATA_DIR,file='all_reformat.json'),
        original_groups=rules.run_poly_spnet.output.groups,
        original_spikes=rules.move_.output.spikes,
        reformat_groups=rules.find_groups.output.original
    run:
        shell('cd {};python make_plots.py -g {} -s {} --prefix {} -w {}'.format(ANA_DIR,input.original_groups,input.original_spikes,'original',input.original_weights))
        shell('cd {};python make_plots.py -g {} -s {} --prefix {} -w {}'.format(ANA_DIR,input.reformat_groups,input.original_spikes,'reformat',input.original_weights))
        for group,weight,spike in zip(input.nest_groups,input.nest_weights,input.nest_spikes):
            shell('cd {};python make_plots.py -g {} -s {} --prefix {} -w {}'.format(ANA_DIR,group,spike,weight.split('_')[0].split('/')[-1],weight))





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