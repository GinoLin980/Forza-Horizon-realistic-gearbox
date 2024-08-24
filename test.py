# from typing import Deque, Dict
from collections import deque
import matplotlib.pyplot as plt

new_records = [
    None
]

dr = deque(new_records, maxlen=2)

print(dr)

def new_data(data: dict[str: int|float]):
    if None in dr or data['rpm'] > dr[-1]['rpm']:
        dr.append(data)

new_data({'rpm': 1400, 'hp': 65, 'torque': 230})
new_data({'rpm': 1400, 'hp': 70, 'torque': 230})

for i in dr:
    print(i)

hps = deque(maxlen=2)

for hp in dr:
    hps.append(hp["hp"])

# import matplotlib.pyplot as plt
# from collections import deque
# import numpy as np

# # Initialize deque
# hps = deque([3, 4], maxlen=2)

# # Plot initial data
# plt.plot([1, 2], hps, c='r')
# hps.append(5)
# plt.plot([2, 3], hps, c='r')
# hps.append(9)
# plt.plot([3, 4], hps, c='r')
# hps.append(7)
# plt.plot([4, 5], hps, c='r')

# # Get the current axis
# ax = plt.gca()

# # Extract data points from all lines
# x_values = []
# y_values = []
# for i, line in enumerate(ax.lines):
#     data = line.get_xydata()
#     if i == 0:
#         x_values.extend(data[:, 0])
#         y_values.extend(data[:, 1])
#     else:
#         print(data[1, 0])
#         print(data[1, 1])
#         x_values.append(data[1, 0])
#         y_values.append(data[1, 1])
#     print(f"Extracted data points from line {i}: {data}")

# # Sort the data by x values to ensure continuity
# x_values = np.array(x_values)
# y_values = np.array(y_values)

# print(x_values)
# print(y_values)

plt.show()


