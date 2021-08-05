#!/bin/bash
# Sends a bsub job for every sid-deck listed in a the input file
# to run the io timeseries
#
# Main paths are set with the configuration file run at the beginning (setenv0.sh)
#
# sid_deck_list_file is: sid-dck yyyy-mm yyyy-mm
#
# Usage: ./report_io_launcher.sh release update dataset level outdir sid_deck_periods_file list_file

# data_dir will be from the env variable, as this is set in the processing chain
# however outdir depends on the plots being on a release or a merge of releases
# We will probably change all this to a json when we have to merge releases!

source ../setpaths.sh
source ../setenv0.sh

release=$1
update=$2
dataset=$3
level=$4
outdir=$(readlink --canonicalize  $5)
sid_deck_periods_file=$(readlink --canonicalize  $6)
sid_deck_list_file=$(readlink --canonicalize  $7)

ffs="-"
filebase=$(basename $sid_deck_list_file)
log_dir=$outdir/log
log_file=$log_dir/io$ffs${filebase%.*}$ffs$(date +'%Y%m%d_%H%M').log

echo $log_file

exec > $log_file 2>&1
# These are default, maybe should be parameterized to boost job submission when small sid-dcks....
job_time=04:00
job_memo=4000
# Now loop through the list of sid-dks in the list, find its l1a config and
# send jobs for the monthly files
for sid_deck in $(awk '{print $1}' $sid_deck_list_file)
do

  # Re-initialize scratch directory for deck
  sid_deck_scratch_dir=$scratch_directory/io/$sid_deck
  echo "Setting deck reports scratch directory: $sid_deck_scratch_dir"
  rm -rf $sid_deck_scratch_dir;mkdir -p $sid_deck_scratch_dir

  echo $sid_deck
	echo $sid_deck_scratch_dir
	bsub -J $sid_deck'IO' -oo $sid_deck_scratch_dir/'IO.o' -eo $sid_deck_scratch_dir/'IO.o' -q short-serial -W $job_time -M $job_memo -R "rusage[mem=$job_memo]" python $um_code_directory/data_summaries/report_io.py $data_directory $release $update $dataset $level $sid_deck $sid_deck_periods_file $outdir/$sid_deck

done
