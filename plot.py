#!/usr/bin/python
"""
    @file plot.py
    @brief Plots discharge profiles captured with bash script
    @note CSV file has no headings, so the order of columns can't be changed!

"""

import csv
import matplotlib.pyplot as plt
import numpy as np


# Main class
class battery_plot:

    # Since the CSV file has no headings, these indices
    # define in which column to find the relevant information
    timestamp_index=0
    status_index=1
    energy_now_index=3

    """
        @brief finds where discharge phases begin and where they end
        @param data list array of the read CSV file, with elements "time,status,X,energy_now,..."
        @returns list of [begin,end] discharge phases
    """
    def __find_discharge_phase (self, data):
        transitions = [] # [[begin, end], [begin,end]] where begin and end are timestamps in unix time
        previous_row = data[0]

        # Flag to indicate if we are in discharging phase
        discharging = False
        
        for row in data:
            
            # Set flag if first or last row
            first_row = (data[0] == row)
            last_row = (data[-1] == row)
            
            if (not discharging): # Not currently in discharge phase, so look for begin transitions
                
                # Four possibilies to start a discharge phase:
                #
                # - Switching from Full to Discharge (removing the charger)
                # - Switching from Charging to Discharge (removing the charger)
                # - Switching from Unknown to Discharge (???)
                # - Starting off discharging (began logging while on battery)
                
                if ((previous_row[self.status_index] == 'Full' and row[self.status_index] == 'Discharging') or
                   (previous_row[self.status_index] == 'Charging' and row[self.status_index] == 'Discharging') or 
                   (previous_row[self.status_index] == 'Unknown' and row[self.status_index] == 'Discharging') or
                   (row[self.status_index] == 'Discharging' and first_row)):
                   
                    discharging = True;
                    start_time = int(row[self.timestamp_index]) # memorize time discharge phase started
                
            else: # Currently in discharge phase, looking for end transitions
                
                # Four possibilities to end a discharge phase:
                #
                # - Switching from Discharging to Charging (plugging in charger)
                # - Switching from Discharging to Full (doesn't really make much sense but happens sometimes?)
                # - Encountering an energy value that has increased (the device was powered down, charged, and powered back up)
                # - Reaching the end of the log file

                if ((previous_row[self.status_index] == 'Discharging' and row[self.status_index] == 'Charging') or # Switched from Discharge to Charging
                    (previous_row[self.status_index] == 'Discharging' and row[self.status_index] == 'Full') or # Switched from Discharge to Full
                     (int(previous_row[self.energy_now_index]) < int(row[self.energy_now_index]))): # Energy is now larger than before
                    
                    # It may be the case that a discharge cycle ends and a new one begin at the same time
                    # this happens if charger was only connected when the device was off
                    if (int(previous_row[self.energy_now_index]) < int(row[self.energy_now_index]) and row[self.status_index] == 'Discharging'):
                        end_time = int(previous_row[self.timestamp_index])
                        transitions.append([start_time, end_time]) # old cycle
                        start_time = int(row[self.timestamp_index]) # start new cycle
                        discharging = True;
                    
                    else :
                        discharging = False;
                        end_time = int(previous_row[self.timestamp_index])
                        transitions.append([start_time, end_time])

                # This is separate because we want to include the last line,
                # where above we do not
                if (row[self.status_index] == 'Discharging' and last_row): # end of file
                   discharging = False;
                   end_time = int(row[self.timestamp_index])
                   transitions.append([start_time,end_time])
                
            previous_row=row

        return transitions

    """
        @brief Reads filename and stores its content in a list
        @returns data Contents of read CSV file

    """
    def __read_file(self, filename):
        with open(filename, 'r') as file:

            # Open log file (is in CSV format)
            reader = csv.reader(file,delimiter=',')

            # Put data into a list
            data = list(reader)
            for row in reader:
                data.append(row)
    
        return data

    """
        @brief Plots the data, one plot for each discharge phase

    """
    def plot (self, filename):
        data = self.__read_file(filename)
        
        # Find when a discharge cycle starts and ends
        discharge_phase = self.__find_discharge_phase(data)
        print('Found', len(discharge_phase), 'discharge phases.')
        if (len(discharge_phase) == 0):
            return 1

        print(discharge_phase)

        # Go through all discharge phases and make a plot for each
        for i in range(0,len(discharge_phase)):
            phase = discharge_phase[i]
            start_time = phase[0] # Begin of discharge phase in unix time
            end_time = phase[1] # End of discharge phase in unix time
            
            previous_time = start_time # To keep track of gaps in the data
            relative_time = 0 # Relative time which begins at 0 when discharge cycle begins
            
            # Arrays for plotting
            energy = [] 
            time = []
            for row in data: # Go through all the data to find the discharge cycle we want
                
                if (int(row[self.timestamp_index]) >= start_time and int(row[self.timestamp_index]) <= end_time): # If in the time frame of interest
                    if ((int(row[self.timestamp_index])-previous_time) < 120): # We allow for a maximum gap size of 120 s
                        
                        relative_time += (int(row[self.timestamp_index])-previous_time)
                        time.append(relative_time/60) # convert from seconds to minutes
                        energy.append(int(row[self.energy_now_index])/1e6) # convert from uWh to Wh
                
                previous_time=int(row[self.timestamp_index])
            
            # Print out total discharge time and start and end energies to the command line
            print('[ Phase',i,'] Total discharge time was','{:.2f}'.format(relative_time/3600),'h',
                 '(','{:.2f}'.format(max(energy)),'Wh ->','{:.2f}'.format(min(energy)),'Wh )')

            # Do the actual plotting
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
        return 0

def main ():
    pl=battery_plot()
    pl.plot('BAT0.log')

if __name__ == "__main__":
        main()

