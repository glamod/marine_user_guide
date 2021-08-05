# -*- coding: utf-8 -*-
"""
Spyder Editor

The following fails because the LSF_output_file and the job_log are in different mounts:
os.rename(LSF_output_file,job_log)
OSError: [Errno 18] Invalid cross-device link:

Have to cp and then remove!

This is a temporary script file.
"""
import os
import sys
import json
import shutil

FFS='-'

# GET INPUT ARGUMENTS
configfile =  sys.argv[1]
exit_status = sys.argv[2]
rm_input = sys.argv[3]

input_basename = os.path.basename(configfile).split('.')[0]
LSF_output_path = os.path.dirname(configfile)
LSF_output_file = os.path.join(LSF_output_path,input_basename + '.o')
run_id = '-'.join(input_basename.split('-')[1:])

# GET INFO FROM CONFIG FILE
with open(configfile,'r') as fO:
    config = json.load(fO) 

yyyy = config.get('year')
mm = config.get('month')

# RENAME AND MOVE LSF OUTFILE
ext='ok' if exit_status == '0' else 'failed'
job_log_file = FFS.join([str(yyyy),str(mm),run_id]) + '.' + ext
job_log =  os.path.join(LSF_output_path,job_log_file)
shutil.copy(LSF_output_file,job_log)
os.remove(LSF_output_file)

# REMOVE *.input FILE
if rm_input == '0':
    os.remove(configfile)
