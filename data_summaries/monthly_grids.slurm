#!/bin/bash
# Runs the pyscript that does the aggregations in monthly lat/lon grids 
#
# Calling sequence:
# ./monthly_grids.slurm version script_config_file

# ------------------------------------------------------------------------------
queue=short-serial
t=10:00:00
mem=5000
om=truncate
# ------------------------------------------------------------------------------
source ../setpaths.sh
source ../setenv.sh

# Here make sure we are using fully expanded paths, as some may be passed to a config file
version=$1
script_config_file=$(readlink --canonicalize $2)

pyscript="$mug_code_directory/data_summaries/monthly_grids.py $script_config_file"
log_dir=$mug_data_directory/$version/level2/log
if [ ! -d $log_dir ]
then
  echo "LOG dir does not exist: $log_dir"
  exit
fi

echo "LOG directory is $log_dir"

for table in header observations-sst observations-at observations-dpt observations-wd observations-ws observations-slp
do

  J=$table
  log_file=$log_dir/$(basename $script_config_file .json)-$table".ok"
  if [ -f "$log_file" ];then rm $log_file;fi
  failed_file=$log_dir/$(basename $script_config_file .json)-$table".failed"
  if [ -f "$failed_file" ];then rm $failed_file;fi

  jid=$(sbatch -J $J -o $log_file -e $log_file -p $queue -t $t --mem $mem --open-mode $om --wrap="python $pyscript $table")
  sbatch --dependency=afternotok:${jid##* } --kill-on-invalid-dep=yes -p $queue -t 00:05:00 --mem 1 --open-mode $om --wrap="mv $log_file $failed_file"
done
