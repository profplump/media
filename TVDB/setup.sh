#!/bin/sh

# Paths
BASE_DIR="."
ENV_DIR="${BASE_DIR}/venv"
PY="python3"

# Setup venv and install our libs
if [ ! -d "${ENV_DIR}" ]; then
  "${PY}" -m venv "${ENV_DIR}"
fi
source "${ENV_DIR}/bin/activate"
"${PY}" -m pip install --user tvdb_v4_official

# Prompt the user
echo
echo source "${ENV_DIR}/bin/activate"
