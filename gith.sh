#!/bin/bash

# Get the directory path of the shell script
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# Change to the script's directory
cd "$SCRIPT_DIR"

python gith.py "${@:1}"
