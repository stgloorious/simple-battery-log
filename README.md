# simple-battery-log
#### Scripts to log and plot battery energy level on Linux systems. 

Bash script fetches battery status at `/sys/class/power_supply` and writes it to a file.
Python script parses the created file and creates a plot like this:
![Discharge plot](/plot1.png)

## Setup
I have not tested this on any other machine than my Thinkpad laptop. They may very well be differences 
in how the battery information is stored on your machine, so you will have to adjust for that.

- Clone the repository: `git clone https://github.com/stgloorious/simple-battery-log && cd simple-battery-log`
- Create a cronjob so `log-battery.sh` is executed each minute: `crontab -e`, then enter `* * * * * sh /path/to/log-battery.sh`
- This will write to `$HOME/BAT0.log` each minute. Check if this is the case.
- After sufficient time, you can move `BAT0.log` to the same directory as `plot.py`. Execute the script `./plot.py` and find the plots in png format in the same directory.
