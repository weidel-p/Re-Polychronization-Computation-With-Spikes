import os,glob,sys
sys.path.insert(0, 'code/NEST_model/') #ugly but not sure how to otherwise handle this
from params import *

#Define folders:
CUR_DIR=os.getcwd()
CODE_DIR=os.path.join('.','code')
DATA_DIR=os.path.join('.','data')
nest_prefix='NEST_model'
izhi_prefix='original_model'
NEST_CODE_DIR=os.path.join(CODE_DIR,nest_prefix)
NEST_DATA_DIR=os.path.join(DATA_DIR,nest_prefix)

IZHI_CODE_DIR=os.path.join(CODE_DIR,izhi_prefix)
IZHI_DATA_DIR=os.path.join(DATA_DIR,izhi_prefix)

#compile poly_spnet into a folder because it outputs into ../
IZHI_EXEC_DIR=os.path.join(IZHI_CODE_DIR,'exec')
IZHI_OUTPUT_FILES=['all.dat']
ANA_DIR=os.path.join(CODE_DIR,'analysis')
NEST_SRC_DIR=os.path.join(
            os.path.join(CUR_DIR,CODE_DIR),'nest/nest-simulator')


PREFIX = ['NEST']
WEIGHT_SAMPLES = ['all_{:02d}.json'.format(i) for i in range(1,N_measure+1)]        #define the weights files output to model.py and input to the cpp code
SPIKE_SAMPLES = ['spikes-{:02d}-0.gdf'.format(1002)]        #define the spike files
GROUP_SAMPLES = ['poly_all_{:02d}.json'.format(i) for i in range(1,N_measure+1)]   # define files output of cpp code and input to example_plots.py
PLOT_FILES = ['plot_8.png']
MAN_DIR='manuscript/8538120cqhctwxyjvvn'
FIG_DIR='figures'


rule all:
    input:
        os.path.join(FIG_DIR,'plot_8.png')


rule install_nest:
    output:
        expand('{nest_folder}/instl/bin/nest_vars.sh',nest_folder=NEST_SRC_DIR)
    params:
        nest_dir=NEST_SRC_DIR,
    shell:
        """
        cd {params.nest_dir}
        mkdir -p bld
        mkdir -p instl
        cd bld
        cmake -DCMAKE_INSTALL_PREFIX:PATH={params.nest_dir}/instl -Dwith-python=ON {params.nest_dir}
        make -j8
        make install
        """

rule run_model:
    output:
        expand("{folder}/{file}",folder=NEST_DATA_DIR,file=WEIGHT_SAMPLES),
        expand("{folder}/{file}",folder=NEST_DATA_DIR,file=SPIKE_SAMPLES)
    input:
        model='{folder}/model.py'.format(folder=NEST_CODE_DIR),
        nest=rules.install_nest.output
    shell:
        """
        source {{input.nest}}
        cd {folder}
        python model.py -o {output_folder}
        """.format(folder=NEST_CODE_DIR,output_folder=NEST_DATA_DIR)

rule reformat_izhi:
    input:
        expand('{folder}/all.dat',folder=IZHI_DATA_DIR),
        expand('{folder}/reformat',folder=ANA_DIR)

    output:
        expand('{folder}/all_reformat.json',folder=IZHI_DATA_DIR)
    shell:
        '{folder}/reformat {{input[0]}} {{output}}'.format(folder=ANA_DIR)


rule compile_reformat:
    input:
        expand('{folder}/reformat.cpp',folder=ANA_DIR)
    output:
        expand('{folder}/reformat',folder=ANA_DIR)
    shell:
        'g++ -o {output} {input} -ljsoncpp'

rule compile_find_polychronous_groups:
	output:
	    expand('{folder}/find_polychronous_groups',folder=ANA_DIR)
	input:
	    expand('{folder}/find_polychronous_groups.cpp',folder=ANA_DIR)
	shell:
	    'g++ -o {output} {input} -ljsoncpp'

rule find_groups:
    output:
        nest=expand("{folder}/{file}",folder=NEST_DATA_DIR,file=GROUP_SAMPLES),
        original=expand("{folder}/reformat_groups.json",folder=IZHI_DATA_DIR)
    input:
        program=rules.compile_find_polychronous_groups.output,
        nest=rules.run_model.output[:-1],
        original=rules.reformat_izhi.output
    run:
        shell('{input.program} {input.original} {output.original}')
        for job in zip(input.nest,output.nest):
            shell('{{input.program}} {} {}'.format(job[0],job[1]))

rule run_and_move_poly_spnet:
    input:
        expand('{folder}/poly_spnet',folder=IZHI_EXEC_DIR)
    output:
        expand('{folder}/{file}',folder=IZHI_DATA_DIR,file=IZHI_OUTPUT_FILES)
    shell:
        """
        cd {folder}
        ./poly_spnet
        cd ..
        mv *.dat {mv_folder}
        """.format(folder=IZHI_EXEC_DIR,mv_folder=IZHI_DATA_DIR)


rule compile_poly_spnet:
    input:
        expand('{folder}/poly_spnet.cpp',folder=IZHI_CODE_DIR)
    output:
        expand('{folder}/poly_spnet',folder=IZHI_EXEC_DIR)
    shell:
        """
        mkdir -p {folder}
        echo {{output}}
	    g++ -o {{output}} {{input}} -ljsoncpp
	    """.format(folder=IZHI_EXEC_DIR)



rule make_plots:
    output:
        expand("{folder}/{file}",folder=FIG_DIR,file=PLOT_FILES)
    input:
        expand("{folder}/{file}",folder=NEST_DATA_DIR,file=GROUP_SAMPLES)
    shell:
        'cd {folder};python make_plots.py '.format(folder=ANA_DIR)



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