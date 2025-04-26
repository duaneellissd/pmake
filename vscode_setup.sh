#! /bin/bash
set -e

THIS_DIR=`dirname ${BASH_SOURCE[0]}`
VENV_DIR=${THIS_DIR}/venv

bash ./venv_create.sh
bash ./venv_add_pmake.sh

source ${VENV_DIR}/bin/activate

python -m pip install -r ${THIS_DIR}/requirements.txt



