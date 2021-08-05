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
import shutil

FFS='-'

# GET INPUT ARGUMENTS
LSF_output_file =  sys.argv[1]
exit_status = sys.argv[2]

run_id = os.path.basename(LSF_output_file).split('.')[0]
LSF_output_path = os.path.dirname(LSF_output_file)

# RENAME AND MOVE LSF OUTFILE
ext='ok' if exit_status == '0' else 'failed'
job_log_file = run_id + '.' + ext
job_log =  os.path.join(LSF_output_path,job_log_file)
shutil.copy(LSF_output_file,job_log)
os.remove(LSF_output_file)
