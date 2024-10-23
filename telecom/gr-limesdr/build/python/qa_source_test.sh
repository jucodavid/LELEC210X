#!/usr/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir="/mnt/d/EPL/Q7/ProjetElec/Project/LELEC210X/telecom/gr-limesdr/python"
export GR_CONF_CONTROLPORT_ON=False
export PATH="/mnt/d/EPL/Q7/ProjetElec/Project/LELEC210X/telecom/gr-limesdr/build/python":$PATH
export LD_LIBRARY_PATH="":$LD_LIBRARY_PATH
export PYTHONPATH=/mnt/d/EPL/Q7/ProjetElec/Project/LELEC210X/telecom/gr-limesdr/build/swig:$PYTHONPATH
/usr/bin/python3 /mnt/d/EPL/Q7/ProjetElec/Project/LELEC210X/telecom/gr-limesdr/python/qa_source.py 
