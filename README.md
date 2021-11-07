# simple-battery-log
#### Scripts to log and plot battery energy level on Linux systems. 

Bash script fetches battery status at `/sys/class/power_supply` and writes it to a file.
Python script parses the created file and creates a plot like this:
![Discharge plot](/plot1.png)

## Setup
I have not tested this on any other machine than my Thinkpad laptop. Likely there will be differences 
in how the battery information is stored on your machine, so you will have to adjust for that.
Make sure `/sys/class/power_supply/BAT0` exists and `energy_now` and  `status` are in the same format as the example below.

- Clone the repository: `git clone https://github.com/stgloorious/simple-battery-log && cd simple-battery-log`
- Create a cronjob so `log-battery.sh` is executed each minute: `crontab -e`, then enter `* * * * * sh /path/to/log-battery.sh`
- This will write to `$HOME/BAT0.log` each minute. Check if this is the case, make sure you can execute the script manually if not.
- After sufficient time, you can move `BAT0.log` to the same directory as `plot.py`. Execute the script `./plot.py` and find a plot for every discharge phase recorded in png format in the same directory.

## Dependencies
You will need:

- Python 3 with csv, matplotlib and numpy
- Basic linux utilities (bash, date, echo etc.)

## Remarks
On my system, the output file `BAT0.log` looks like this:

    1636047661,Discharging,45090000,34660000
    1636047721,Discharging,45090000,34610000
    1636047781,Discharging,45090000,34520000

Where the first column indicates the current unix time, the second indicates the battery status with the values 'Charging', 'Discharging', or 'Full', followed by the maximum energy of the battery in uWh, followed by the current energy of the battery in uWh. The scripts are designed to work with these kinds of values. In the current version, the maximum energy is ignored.

Tested and developed on Gentoo Linux with Kernel version 5.10.61-gentoo-x86_64
