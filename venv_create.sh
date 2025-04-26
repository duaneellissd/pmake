#! /bin/bash

THIS_SCRIPT=${BASH_SOURCE[0]}
THIS_DIR=`dirname $THIS_SCRIPT`

VENV_DIR=${THIS_DIR}/venv
if [ -d ${VENV_DIR} ]
then
    rm -rf ${VENV_DIR}
fi

python3 -m venv ${VENV_DIR}

