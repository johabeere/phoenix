#!/bin/bash
export LIBCAMERA_LOG_LEVELS="3"
RPI_LGPIO_CHIP="0"
source ./venv/bin/activate
while true; do
    clear
    python Main.py
    RETURN_VALUE=$?

    if [ $RETURN_VALUE -ne 3 ]; then
        break
    fi
done
deactivate