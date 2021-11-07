#!/usr/bin/python
"""
    @file plot.py
    @brief Plots discharge profiles captured with bash script
    @note CSV file has no headings, so the order of columns can't be changed!

"""

import csv
import matplotlib.pyplot as plt
import numpy as np

"""
    @brief finds where discharge phases begin and where they end
    @param data list array of the read CSV file, with elements "time,status,X,energy_now,..."
    @returns list of [begin,end] discharge phases
"""
def find_discharge_phase (data):
    transitions = []
    previous_row = data[0]

    # Flag to indicate if we are in discharging phase
    discharging = False
    for row in data:
        # Set flag if first or last row
        first_row = (data[0] == row)
        last_row = (data[-1] == row)
        if (not discharging): # Not currently in discharge phase, so look for begin transitions
            # Three possibilies of starting a discharge phase:
            if ((previous_row[1] == 'Full' and row[1] == 'Discharging') or # Switched from Full to Discharge
                (row[1] == 'Discharging' and first_row) or # Started off discharging
                (previous_row[1] == 'Charging' and row[1] == 'Discharging')): # Switched from Charging to Discharge
                discharging=True;
                start_time=int(row[0]) # memorize time discharge phase started
                
        else: # Currently in discharge phase, looking for end transitions
            if ((previous_row[1] == 'Discharging' and row[1] == 'Charging') or # Switched from Discharge to Charging
                (int(previous_row[3])<int(row[3]))): # Energy is now larger than before
                discharging=False;
                end_time=int(row[0]) # memorize time discharge phase started
                transitions.append([start_time,end_time])
            
        previous_row=row
    return transitions

"""
    @brief Reads data from file and plots it

"""
def main ():
    with open('BAT0.log', 'r') as file:

        # Open log file (is in CSV format)
        reader = csv.reader(file,delimiter=',')

        # Put data into a list
        data=list(reader)
        for row in reader:
            data.append(row)
        # All fields are stored as a string

    # Find when a discharge cycle starts and ends
    discharge_phase=find_discharge_phase(data)
    print('Found', len(discharge_phase), 'discharge phases.')

    # Go through all discharge phases and make a plot for each
    for i in range(0,len(discharge_phase)):
        phase=discharge_phase[i]
        start_time=phase[0] # Begin of discharge phase in unix time
        end_time=phase[1] # End of discharge phase in unix time
        
        previous_time=start_time # To keep track of gaps in the data
        relative_time=0 # Relative time which begins at 0 when discharge cycle begins
        
        # Arrays for plotting
        energy = [] 
        time = []
        for row in data: # Go through all the data to find the discharge cycle we want
            if (int(row[0]) >= start_time and int(row[0]) <= end_time):
                if ((int(row[0])-previous_time) < 120): # We allow for a maximum gap size of 120 s
                    relative_time += (int(row[0])-previous_time)
                    time.append(relative_time/60)
                    energy.append(int(row[3])/1e6)
            previous_time=int(row[0])
        print('[ Phase',i,'] Total discharge time was','{:.2f}'.format(relative_time/3600),'h',
             '(','{:.2f}'.format(max(energy)),'Wh ->','{:.2f}'.format(min(energy)),'Wh )')

        plt.figure(figsize=(20,10),facecolor='white')
        plt.title('Discharge profile '+str(i)+', '+'{:.2f}'.format(relative_time/3600)+' h, '+
                  '{:.2f}'.format(max(energy))+' Wh -> '+'{:.2f}'.format(min(energy))+' Wh',fontsize=28)
        plt.xticks(np.arange(0, max(time), 30),fontsize=16)
        plt.yticks(np.arange(0, max(energy), 5),fontsize=16)
        plt.xlabel('Time [min]',fontsize=16)
        plt.ylabel('Energy [Wh]',fontsize=16)
        plt.grid()
        plt.plot(time,energy,'-o',ms=3,color='red')
        plt.savefig('plot'+str(i)+'.png')
        
    print('Exported plot(s) as png file(s). Goodbye.')


if __name__ == "__main__":
        main()
