
# WATCH THIS HARCODING UNTIL WE DECIDE WHAT TO DO WITH REPOS AND ENVS!
pyEnvironment_directory=$mug_code_directory/env/mug_env
# Activate python environment and add jaspy3.7 path to LD_LIBRARY_PATH so that cartopy and other can find the geos library
source $pyEnvironment_directory/bin/activate
export PYTHONPATH="$mug_code_directory:${PYTHONPATH}"
export LD_LIBRARY_PATH=/apps/contrib/jaspy/miniconda_envs/jaspy3.7/m3-4.5.11/envs/jaspy3.7-m3-4.5.11-r20181219/lib/:$LD_LIBRARY_PATH
echo "Python environment loaded from gws: $pyEnvironment_directory"
