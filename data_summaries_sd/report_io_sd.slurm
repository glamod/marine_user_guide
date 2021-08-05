#!/bin/bash
# Runs the pyscript that does the monthly counts of header table quality
# indicators on every source-deck partition
#
# log dir does not need to exist
#
# Calling sequence:
# ./report_io_sd.slurm log_dir script_config_file process_list

# ------------------------------------------------------------------------------
queue=short-serial
t=01:00:00
mem=500
om=truncate
# ------------------------------------------------------------------------------
source ../setpaths.sh
source ../setenv.sh

# Here make sure we are using fully expanded paths, as some may be passed to a config file
log_dir=$(readlink --canonicalize $1)
script_config_file=$(readlink --canonicalize $2)
process_list=$(readlink --canonicalize $3)

pyscript=$mug_code_directory/data_summaries_sd/report_io_sd.py
if [ ! -d $log_dir ]
then
  echo "LOG dir does not exist: $log_dir"
  exit
fi

for sid_dck in $(awk '{print $1}' $process_list)
do
  log_dir_sd=$log_dir/$sid_dck
  if [ ! -d $log_dir_sd ]
  then
    echo "$sid_dck LOG dir does not exist: $log_dir_sd"
    exit
  fi
  J=$sid_dck
  log_file=$log_dir_sd/$(basename $script_config_file .json)".ok"
  if [ -f "$log_file" ];then rm $log_file;fi
  failed_file=$log_dir_sd/$(basename $script_config_file .json)".failed"
  if [ -f "$failed_file" ];then rm $failed_file;fi
  jid=$(sbatch -J $J -o $log_file -e $log_file -p $queue -t $t --mem $mem --open-mode $om --wrap="python $pyscript $sid_dck $script_config_file")
  sbatch --dependency=afternotok:${jid##* } --kill-on-invalid-dep=yes -p $queue -t 00:05:00 --mem 1 --open-mode $om --wrap="mv $log_file $failed_file"
done
