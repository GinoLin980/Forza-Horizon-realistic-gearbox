import os
import keyboard as k
import math
try:
    os.system('cls')
except:
    os.system('clear')

# change gas_thresholds here
# define the settings for different driving modes
# 0 index is : used in agressiveness increase decision
# 1 index is : used in agressiveness increase decision
# 2 index is : how quickly the aggressiveness lowers when driving calmly (1/value)
# 3 index is : the bare minimum aggressiveness to keep at any given time
gas_thresholds = [1, 0.5, 6, 0.12] # Eco mode

# [0.95, 0.3, 12, 0.12] # Normal mode
# [0.8, 0.4, 24, 0.25] # Sports mode
# [1, 0.5, 6, 0.12] # Eco mode


# adjust the rpm if needed
idleRPM = 1265.6243896484375
maxShiftRPM = 7309.99580078125

gas = 0
brake = 0

while True:
    abc = input('Gas: ')
    if abc == '1':
        gas = 0.1
        try:
            os.system('cls')
        except:
            os.system('clear')


    elif abc == '2':
        gas = 0.2
        try:
            os.system('cls')
        except:
            os.system('clear')


    elif abc == '3':
        gas = 0.3
        try:
            os.system('cls')
        except:
            os.system('clear')


    elif abc == '4':
        gas = 0.4
        try:
            os.system('cls')
        except:
            os.system('clear')


    elif abc == '5':
        gas = 0.5
        try:
            os.system('cls')
        except:
            os.system('clear')


    elif abc == '6':
        gas = 0.6
        try:
            os.system('cls')
        except:
            os.system('clear')


    elif abc == '7':
        gas = 0.7
        try:
            os.system('cls')
        except:
            os.system('clear')

    elif abc == '8':
        gas = 0.8
        try:
            os.system('cls')
        except:
            os.system('clear')

    elif abc == '9':
        gas = 0.9
        try:
            os.system('cls')
        except:
            os.system('clear')

    elif abc == '0':
        gas = 1
        try:
            os.system('cls')
        except:
            os.system('clear')

    elif abc == 'q':
        quit()
        

    gas_calculation = round((gas - gas_thresholds[1]) / (gas_thresholds[0] - gas_thresholds[1])*1.5, 4)
    brake_calculation = round((brake - (gas_thresholds[1] - 0.3)) / (gas_thresholds[0] - gas_thresholds[1]) * 1.6, 4)


    new_aggr =  round(min(1, max(gas_calculation, brake_calculation)), 4)
    
    print(f"Gas calculation: {gas_calculation}")
    print(f"Brake calculation: {brake_calculation}")
    print(f"Biggest: {"Gas" if gas_calculation > brake_calculation else "Brake"} ({new_aggr})")

    new_aggr = max(new_aggr, gas_thresholds[3])
    rpmRangeTop = round((idleRPM + 50 + ((maxShiftRPM - idleRPM - 400) * new_aggr)), 4)
    rpm_added = round(((maxShiftRPM - idleRPM - 400) * new_aggr * 0.95), 4)
    
    print("\n")
    print(f"Final aggressiveness: {new_aggr}")
    print(f"RPM Range Top: {rpmRangeTop} ({rpm_added} added)")
    
    
