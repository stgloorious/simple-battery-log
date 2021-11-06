#!/bin/bash

# Fetches current energy of BAT and writes it to a file, 
# together with the maximum energy of the battery and 
# the current date
#
# Execute this script at regular intervals, e.g. with a cronjob
# If you plan to run this continously, also configure logrotate 
# or delete/archive old log files manually

OUTPUT_DIR=$HOME
BAT="BAT0"
BATPATH="/sys/class/power_supply"

# Fetch relevant data
DATE=$(date +%s) # date now in unix time
E_NOW=$(cat $BATPATH/$BAT/energy_now)
E_FULL=$(cat $BATPATH/$BAT/energy_full) # note that this is different from design capacity
STATUS=$(cat $BATPATH/$BAT/status) # is "Discharging", "Charging" or "Full"

# Log to file
echo "$DATE,$STATUS,$E_FULL,$E_NOW" >> "$OUTPUT_DIR/$BAT.log";

exit 0;

