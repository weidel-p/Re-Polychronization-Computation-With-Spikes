#!/usr/bin/env bash
#SBATCH --mail-type=END,FAIL # notifications for job done & fail

snakemake --jobs 300\
          --cluster "sbatch -n {cluster.N} --time {cluster.time}"\
          --cluster-config cluster.json\
          --jobname "{jobid}.{rulename}"\
          &>snakelog.log

