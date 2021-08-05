#!/bin/bash

#. FUNCTIONS -------------------------------------------------------------------
# Get JOB
function nk_jobid {
    output=$($*)
    echo $output | head -n1 | cut -d'<' -f2 | cut -d'>' -f1
}
# ------------------------------------------------------------------------------
source ../setpaths.sh
source ../setenv0.sh

# Here make sure we are using fully expanded paths, as some may be passed to a config file
nc_dir=$(readlink --canonicalize  $1)
out_dir=$(readlink --canonicalize  $2)
config_file=$(readlink --canonicalize  $3)
process_list_file=$(readlink --canonicalize  $4)

pyscript=$um_code_directory/figures/nc_to_map.py
pyhdlr=$um_code_directory/figures/process_output_hdlr.py
run_id=$(basename $config_file .json)

job_time_hhmm=01:00
job_memo_mbi=8000

for sid_dck in $(awk '{print $1}' $process_list_file)
do
   sid_dck_log_dir=$nc_dir/log/$sid_dck
   sid_dck_nc_dir=$nc_dir/$sid_dck
   sid_dck_out_dir=$out_dir/$sid_dck
   sid_dck_scratch_dir=$scratch_directory/nc_to_map/$sid_dck
   echo "Setting deck reports scratch directory: $sid_dck_scratch_dir"
   rm -rf $sid_dck_scratch_dir;mkdir -p $sid_dck_scratch_dir

   jobid=$(nk_jobid bsub -J $sid_dck -oo $sid_dck_log_dir/$run_id".o" -eo $sid_dck_log_dir/$run_id".o" -q short-serial -W $job_time_hhmm -M $job_memo_mbi -R "rusage[mem=$job_memo_mbi]" python $pyscript $sid_dck_nc_dir $sid_dck_out_dir $config_file)

   # Add this when hdlrs homogeneized
   #bsub -J OK -w "done($jobid)" -oo $sid_deck_scratch_dir/$run_id".ho" -eo $sid_deck_scratch_dir/$run_id".ho" -q short-serial -W 00:01 -M 10 -R "rusage[mem=10]" \
   #python $pyhdlr $sid_dck_log_dir/$run_id".o" 0 1

   #bsub -J ER -w "exit($jobid)" -oo$sid_deck_scratch_dir/$run_id".ho" -eo $sid_deck_scratch_dir/$run_id".ho" -q short-serial -W 00:01 -M 10 -R "rusage[mem=10]" \
   #python $pyhdlr $sid_dck_log_dir/$run_id".o" 1 1
done
