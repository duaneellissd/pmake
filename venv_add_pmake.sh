#! /bin/bash

# Where is this file? And what directory is it located in?
THIS_SCRIPT=${BASH_SOURCE[0]}
THIS_DIR=`dirname $THIS_SCRIPT`

# Sanity check: We expect the python virtual env to be in this directory.
VENV_DIR=${THIS_DIR}/venv
if [ ! -d ${VENV_DIR} ]
then
    echo "Cannot find VENV directory: ${VENV_DIR}"
    exit 1
fi

# Sanity check: And we should find the cfg file here
file=${VENV_DIR}/pyvenv.cfg
if [ ! -f ${file} ]
then
    echo "Cannot find ${file}"
    exit 1
fi

# Where do we keep our local modules
# that are *NOT* *YET* installed
LOCAL_MODULES_DIR=${THIS_DIR}/local_modules

# Sanity check.
if [ ! -d ${LOCAL_MODULES_DIR}/pmake ]
then
    echo "Cannot find local pmake module in: ${OUR_LOCAL_MODULES_DIR}"
    exit 1
fi

# Make our local modules visible in the Virutal Enviornment.
# We do this for every version of Python in the VENV.
for site_dir in ${VENV_DIR}/lib/python*/site-packages
do
    tmp=`realpath ${LOCAL_MODULES_DIR}`
    echo "${tmp}" > ${site_dir}/pmake.pth
done

source ${VENV_DIR}/bin/activate



