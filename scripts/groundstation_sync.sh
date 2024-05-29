#!/bin/bash
while true; do
    rsync -avz debra2@debra2.local:/home/debra2/sx1268/SX1268/src/data/ /home/lemuel/AERO4701/aero4701-gui/data
    sleep 5
done
