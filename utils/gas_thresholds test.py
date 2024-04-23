import os
    
def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')  # for windows
# change gas_thresholds here
# define the settings for different driving modes
# 0 index is : used in aggressiveness increase decision
# 1 index is : used in aggressiveness increase decision
# 2 index is : how quickly the aggressiveness lowers when driving calmly (1/value)
# 3 index is : the bare minimum aggressiveness to keep at any given time
MODES = {
    "Normal": [0.95, 0.35, 12, 0.12],
    "Sports": [0.8, 0.4, 24, 0.35],
    "Eco": [1, 0.35, 6, 0.12],
    "Manual": [0, 0, 0, 0]
}
gas_thresholds = MODES['Normal']


# adjust the rpm if needed
idleRPM = 790
maxShiftRPM = 7000

gas = 0
brake = 0

while True:
    gas_input = input('Gas: ')
    if gas_input == '1':
        gas = 0.1
        clear_screen()


    elif gas_input == '2':
        gas = 0.2
        clear_screen()


    elif gas_input == '3':
        gas = 0.3
        clear_screen()


    elif gas_input == '4':
        gas = 0.4
        clear_screen()


    elif gas_input == '5':
        gas = 0.5
        clear_screen()


    elif gas_input == '6':
        gas = 0.6
        clear_screen()


    elif gas_input == '7':
        gas = 0.7
        clear_screen()

    elif gas_input == '8':
        gas = 0.8
        clear_screen()

    elif gas_input == '9':
        gas = 0.9
        clear_screen()

    elif gas_input == '0':
        gas = 1
        clear_screen()

    elif gas_input == 'q':
        quit()
        
    print(f"({gas} - {gas_thresholds[1]}) / ({gas_thresholds[0]} - {gas_thresholds[1]})*1.5")

    gas_calculation = round((gas - gas_thresholds[1]) / (gas_thresholds[0] - gas_thresholds[1])*1.5, 4)
    brake_calculation = round((brake - (gas_thresholds[1] - 0.3)) / (gas_thresholds[0] - gas_thresholds[1]) * 1.6, 4)

    new_aggr =  round(min(1, max(gas_calculation, brake_calculation)), 4)
    
    print(f"Gas calculation: {gas_calculation}")
    print(f"Brake calculation: {brake_calculation}")
    print(f"Biggest: {"Gas" if gas_calculation > brake_calculation else "Brake"} ({new_aggr})")

    new_aggr = max(new_aggr, gas_thresholds[3])
    rpmRangeTop = round((idleRPM + 650 + ((maxShiftRPM - idleRPM - 400) * new_aggr * 0.95)), 4)
    rpm_added = round(((maxShiftRPM - idleRPM - 400) * new_aggr * 0.95), 4)
    
    print("\n")
    print(f"Final aggressiveness: {new_aggr}")
    print(f"RPM Range Top: {rpmRangeTop} ({rpm_added} added)")
    
    
