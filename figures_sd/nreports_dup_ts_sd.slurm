#!/bin/bash
# Runs the pyscript that does the ts plots with the spatio-temporal coverage
# of the evcs in every source-deck partition
#
# log dir does not need to exist
#
# Calling sequence:
# ./nreports_dup_ts_sd.slurm log_dir script_config_file process_list

# ------------------------------------------------------------------------------
queue=short-serial
t=00:05:00
mem=100
om=truncate
# ------------------------------------------------------------------------------
source ../setpaths.sh
source ../setenv.sh

# Here make sure we are using fully expanded paths, as some may be passed to a config file
log_dir=$(readlink --canonicalize $1)
script_config_file=$(readlink --canonicalize $2)
process_list=$(readlink --canonicalize $3)

pyscript=$mug_code_directory/figures_sd/nreports_dup_ts_sd.py
if [ ! -d $log_dir ]; then mkdir -p $log_dir; fi
echo "LOG DIR IS $log_dir"

for sid_dck in $(awk '{print $1}' $process_list)
do
  log_dir_sd=$log_dir/$sid_dck
  if [ ! -d $log_dir_sd ];then mkdir -p $log_dir_sd; fi
  J=$sid_dck
  log_file=$log_dir_sd/$(basename $script_config_file .json)".ok"
  failed_file=$log_dir_sd/$(basename $script_config_file .json)".failed"
  jid=$(sbatch -J $J -o $log_file -e $log_file -p $queue -t $t --mem $mem --open-mode $om --wrap="python $pyscript $sid_dck $script_config_file")
  sbatch --dependency=afternotok:${jid##* } --kill-on-invalid-dep=yes -p $queue -t 00:05:00 --mem 1 --open-mode $om --wrap="mv $log_file $failed_file"
done
