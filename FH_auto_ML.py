import socket, struct
import pandas as pd
import time, keyboard, torch
from torch import nn



UDP_IP = "127.0.0.1"  # This sets server ip to localhost
UDP_PORT = 8000  # You can freely edit this

MODE = "Normal"

gas = 0
brake = 0
rpm_max = 0
in_first_gear = 0
in_overdrive = 0

last_upshift = time.time() - 6
jump_time = time.time() - 6
count = 0

#reading data and assigning names to data types in data_types dict
data_types = {
    "IsRaceOn": "s32",
    "TimestampMS": "u32",
    "EngineMaxRpm": "f32",
    "EngineIdleRpm": "f32",
    "CurrentEngineRpm": "f32",
    "AccelerationX": "f32",
    "AccelerationY": "f32",
    "AccelerationZ": "f32",
    "VelocityX": "f32",
    "VelocityY": "f32",
    "VelocityZ": "f32",
    "AngularVelocityX": "f32",
    "AngularVelocityY": "f32",
    "AngularVelocityZ": "f32",
    "Yaw": "f32",
    "Pitch": "f32",
    "Roll": "f32",
    "NormalizedSuspensionTravelFrontLeft": "f32",
    "NormalizedSuspensionTravelFrontRight": "f32",
    "NormalizedSuspensionTravelRearLeft": "f32",
    "NormalizedSuspensionTravelRearRight": "f32",
    "TireSlipRatioFrontLeft": "f32",
    "TireSlipRatioFrontRight": "f32",
    "TireSlipRatioRearLeft": "f32",
    "TireSlipRatioRearRight": "f32",
    "WheelRotationSpeedFrontLeft": "f32",
    "WheelRotationSpeedFrontRight": "f32",
    "WheelRotationSpeedRearLeft": "f32",
    "WheelRotationSpeedRearRight": "f32",
    "WheelOnRumbleStripFrontLeft": "s32",
    "WheelOnRumbleStripFrontRight": "s32",
    "WheelOnRumbleStripRearLeft": "s32",
    "WheelOnRumbleStripRearRight": "s32",
    "WheelInPuddleDepthFrontLeft": "f32",
    "WheelInPuddleDepthFrontRight": "f32",
    "WheelInPuddleDepthRearLeft": "f32",
    "WheelInPuddleDepthRearRight": "f32",
    "SurfaceRumbleFrontLeft": "f32",
    "SurfaceRumbleFrontRight": "f32",
    "SurfaceRumbleRearLeft": "f32",
    "SurfaceRumbleRearRight": "f32",
    "TireSlipAngleFrontLeft": "f32",
    "TireSlipAngleFrontRight": "f32",
    "TireSlipAngleRearLeft": "f32",
    "TireSlipAngleRearRight": "f32",
    "TireCombinedSlipFrontLeft": "f32",
    "TireCombinedSlipFrontRight": "f32",
    "TireCombinedSlipRearLeft": "f32",
    "TireCombinedSlipRearRight": "f32",
    "SuspensionTravelMetersFrontLeft": "f32",
    "SuspensionTravelMetersFrontRight": "f32",
    "SuspensionTravelMetersRearLeft": "f32",
    "SuspensionTravelMetersRearRight": "f32",
    "CarOrdinal": "s32",
    "CarClass": "s32",
    "CarPerformanceIndex": "s32",
    "DrivetrainType": "s32",
    "NumCylinders": "s32",
    "HorizonPlaceholder": "hzn",
    "PositionX": "f32",
    "PositionY": "f32",
    "PositionZ": "f32",
    "Speed": "f32",
    "Power": "f32",
    "Torque": "f32",
    "TireTempFrontLeft": "f32",
    "TireTempFrontRight": "f32",
    "TireTempRearLeft": "f32",
    "TireTempRearRight": "f32",
    "Boost": "f32",
    "Fuel": "f32",
    "DistanceTraveled": "f32",
    "BestLap": "f32",
    "LastLap": "f32",
    "CurrentLap": "f32",
    "CurrentRaceTime": "f32",
    "LapNumber": "u16",
    "RacePosition": "u8",
    "Accel": "u8",
    "Brake": "u8",
    "Clutch": "u8",
    "HandBrake": "u8",
    "Gear": "u8",
    "Steer": "s8",
    "NormalizedDrivingLine": "s8",
    "NormalizedAIBrakeDifference": "s8",
}

#assigning sizes in bytes to each variable type
jumps={
    's32': 4, #Signed 32bit int, 4 bytes of size
    'u32': 4, #Unsigned 32bit int
    'f32': 4, #Floating point 32bit
    'u16': 2, #Unsigned 16bit int
    'u8': 1, #Unsigned 8bit int
    's8': 1, #Signed 8bit int
    'hzn': 12 #Unknown, 12 bytes of.. something
}

def get_data(data):
    return_dict={}

    #additional var
    passed_data = data
    
    for i in data_types:
        d_type = data_types[i]#checks data type (s32, u32 etc.)
        jump=jumps[d_type]#gets size of data
        current = passed_data[:jump]#gets data

        decoded = 0
        #complicated decoding for each type of data
        if d_type == 's32':
            decoded = int.from_bytes(current, byteorder='little', signed = True)
        elif d_type == 'u32':
            decoded = int.from_bytes(current, byteorder='little', signed=False)
        elif d_type == 'f32':
            decoded = struct.unpack('f', current)[0]
        elif d_type == 'u16':
            decoded = struct.unpack('H', current)[0]
        elif d_type == 'u8':
            decoded = struct.unpack('B', current)[0]
        elif d_type == 's8':
            decoded = struct.unpack('b', current)[0]
        
        #adds decoded data to the dict
        return_dict[i] = decoded
        
        
        #removes already read bytes from the variable
        passed_data = passed_data[jump:]
    
    
    
    #returns the dict
    return return_dict

def analyze_input():
    global gas, brake, rpm_max, in_first_gear, in_overdrive
    gas = rt["Accel"] / 255
    brake = rt["Brake"] / 255
    rpm_max = (rt["CurrentEngineRpm"] - rt["EngineIdleRpm"]) / (rt["EngineMaxRpm"] - 600)
    in_first_gear = 1 if rt["Gear"] == 1 else 0
    in_overdrive = 1 if rt["Gear"] > 4 else 0

# Create a neural network model for evaluation
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(5, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 128)
        self.fc4 = nn.Linear(128, 128)
        self.fc5 = nn.Linear(128, 3)  # Output layer for shift status (0, 1, 2)
        self.fc6 = nn.Linear(128, 1)  # Output layer for jump gears or not (0 or 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        shift = self.fc5(x)  # Predicts shift status
        jump = self.fc6(x)  # Predicts whether to jump gears or not
        return shift, jump

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# create instance of the model and load model parameters    
model = Net()
model.load_state_dict(torch.load(f'MODELS/first_{MODE}_model.pth'))

while True:
        data, addr = sock.recvfrom(1500)
        rt = get_data(data)

        # stop calculation if not driving or cruising
        if rt["IsRaceOn"] == 0:
            continue
        if rt['Gear'] == 0:
            continue
        if rt['Speed'] < 4:
            continue
        if rt["Accel"] / 255 == 0 and rt["Brake"] / 255 == 0:
            continue

        # save resource by making model evaluation every 30 count
        count += 1
        # print('predicting...' if count % 30 == 0 else 'waiting...', end='\r')

        if count % 30 == 0 and time.time() - last_upshift > 1: # prevent up-down-up-down
            analyze_input()
            model.eval()
            with torch.no_grad():
                shift_logit, jump_logit = model(torch.Tensor([[rpm_max, gas, brake, in_first_gear, in_overdrive]]))
                
                # making raw output into probability
                shift_prob = torch.softmax(shift_logit, dim=1)
                # and choose the highest probability
                shift = torch.argmax(shift_prob, dim=1)

                # making raw output into probability (in binary classification, sigmoid makes a number into float from 0 to 1)
                jump_prob = torch.sigmoid(jump_logit)
                # and choose the highest probability (round makes the number bigger than 0.5 into 1 and vice versa)
                jump = torch.round(jump_prob).squeeze(dim=1)
                print(shift, jump, rpm_max, end='\r')

                if jump == 0:
                    pass
                elif jump == 1:
                    if time.time() - jump_time > 5:
                        for i in range(int((1 - rt['CurrentEngineRpm']/rt['EngineMaxRpm']) / 2.2 * 12)):
                            keyboard.press_and_release('q')
                            time.sleep(0.03)
                        jump_time = time.time()
                if jump == 1:
                    continue
                if shift == 0 and rt['Gear'] > 1:
                    keyboard.press_and_release('q')
                elif shift == 1:
                    pass
                elif shift == 2:
                    keyboard.press_and_release('e')
                    last_upshift = time.time()
                