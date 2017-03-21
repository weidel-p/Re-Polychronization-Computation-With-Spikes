import os,glob,sys
sys.path.insert(0, 'code/model/') #ugly but not sure how to otherwise handle this
from params import *

WEIGHT_SAMPLES = ['all_{:02d}.json'.format(i) for i in range(N_measure)]        #define the weights files output to model.py and input to the cpp code
SPIKE_SAMPLES = ['spikes_{:02d}-0.gdf'.format(1002)]        #define the weights files output to model.py and input to the cpp code

GROUP_SAMPLES = ['poly_all_{:02d}.json'.format(i) for i in range(N_measure)]   # define files output of cpp code and input to example_plots.py
PLOT_FILES = ['plot_5.png','plot_8.png']
MAN_FOLDER='manuscript/8538120cqhctwxyjvvn'
ANA_FOLDER='code/analysis'
MODEL_FOLDER='code/model'
FIG_FOLDER='figures'
NEST_FOLDER='code/nest/nest-simulator'
CUR_FOLDER=os.getcwd()
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


rule make_plots:
    output:
        expand("figures/{file}",file=PLOT_FILES)
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
	    'g++ -o code/analysis/find_polychronous_groups code/analysis/find_polychronous_groups.cpp -ljsoncpp'

rule run_model:
    output:
        expand("data/{file}",file=WEIGHT_SAMPLES),
        expand("data/{file}",file=SPIKE_SAMPLES)
    input:
        'code/model/model.py'
    shell:
        """
        ./{install_nest.output}
        cd code/model/
        python model.py
        """



rule install_nest:
    output:
        expand('{cur_dir}/{nest_folder}/instl/bin/nest_vars.sh',nest_folder=NEST_FOLDER,cur_dir=CUR_FOLDER)
    params:
        nest_dir=NEST_FOLDER,
        cur_dir=CUR_FOLDER
    shell:
        """
        git submodule init
        git submodule update --remote
        cd {params.cur_dir}/{params.nest_dir}
        mkdir -p bld
        mkdir -p instl
        cd bld
        cmake -DCMAKE_INSTALL_PREFIX:PATH={params.cur_dir}/{params.nest_dir}/instl -Dwith-python=ON {params.cur_dir}/{params.nest_dir}
        make -j8
        make install
        make installcheck
        """

# compile polyspnet into subfolder because writout in ../
# run polyspnet
# move data to /data/original_model
# compile reformat.cpp
# run reformat /data/original_model/all.dat /data/original_model/raw_data.json
# compile find_poly
# run find_poly /data/original_model/raw_data.json /data/original_model/groups.json
# exampleplot on data set as input file

# run model.py /data/NEST_model
# run find_poly on nest
# exampleplot on data set as input file

#write things

