import sys; sys.dont_write_bytecode = True
import customtkinter as ctk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from collections import deque
from typing import Deque

# Constants
BACKGROUND_COLOR = "#242424"
NAVIGATION_BACKGROUND = "#656565"
DYNO_DATA: Deque[dict[str: int|float]] | None = deque([None, None], maxlen=2) # initiate with None



class dyno_frame:
    def __init__(self, page):
        # Create a figure with a transparent background
        fig = Figure(figsize=(5, 3), dpi=100, facecolor='none')
        ax = fig.add_subplot(facecolor='none')

        # Set spines, ticks, and labels to white
        for spine in ax.spines.values():
            spine.set_color('white')

        ax.set_xticks(range(0, 1501, 500))
        ax.set_yticks(range(0, 301, 100))

        ax.tick_params(axis='both', colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')

        # Plot an initial blank chart
        ax.plot([], [])

        # Function to update the chart with random curves
        def add_new_power_data(data: dict[str: int|float]):
            if None in DYNO_DATA or data["rpm"] > DYNO_DATA[-1]["rpm"]:
                DYNO_DATA.append(data)
            else:
                update_plot()
        def update_plot():
            # ax.clear()
            rpms = deque([d['rpm'] for d in DYNO_DATA], maxlen=2)
            hps = deque([d['hp'] for d in DYNO_DATA], maxlen=2)
            torques = deque([d['torque'] for d in DYNO_DATA], maxlen=2)
            ax.plot(rpms, hps, color='red', label='Horsepower')
            ax.plot(rpms, torques, color='blue', label='Torque')
            
            ax.tick_params(axis='both', colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            
            # ax.legend(loc='upper left', facecolor=BACKGROUND_COLOR, labelcolor='white')
            ax.relim()
            ax.autoscale_view()
            canvas.draw()

        def clear_chart():
            ax.clear()
            ax.set_xticks(range(0, 3001, 500))
            ax.set_yticks(range(0, 601, 100))
            canvas.draw()

        # def _test_plot():
        #     # Initialize DYNO_DATA with some starting values
        #     DYNO_DATA.clear()
        #     DYNO_DATA.extend([{'rpm': 1000, 'hp': 100, 'torque': 200},
        #                     {'rpm': 1500, 'hp': 120, 'torque': 250}])

        #     # Extract initial data
        #     rpms = deque([d['rpm'] for d in DYNO_DATA], maxlen=2)
        #     hps = deque([d['hp'] for d in DYNO_DATA], maxlen=2)
        #     torques = deque([d['torque'] for d in DYNO_DATA], maxlen=2)

        #     # Create plot lines
        #     hp_line, = ax.plot(rpms, hps, color='red', label='Horsepower')
        #     torque_line, = ax.plot(rpms, torques, color='blue', label='Torque')
        #     ax.legend(loc='upper left', facecolor=BACKGROUND_COLOR, labelcolor='white')

        #     # Update function for animation
        #     def update(i):
        #         # Update data
        #         new_rpm = rpms[-1] * 1.00005
        #         new_hp = hps[-1] * 1.00005
        #         new_torque = torques[-1] * 1.00005
                
        #         rpms.append(new_rpm)
        #         hps.append(new_hp)
        #         torques.append(new_torque)
                
        #         # Limit the length of data
        #         if len(rpms) > 100:  # Keep only the last 100 data points
        #             rpms.pop(0)
        #             hps.pop(0)
        #             torques.pop(0)

        #         # Update plot lines
        #         hp_line.set_data(rpms, hps)
        #         torque_line.set_data(rpms, torques)
                
        #         ax.relim()
        #         ax.autoscale_view()

        #     # Use FuncAnimation to update the plot
        #     from matplotlib.animation import FuncAnimation
        #     ani = FuncAnimation(fig, update, frames=range(8000), repeat=False, interval=50)

        #     # Draw the canvas
        #     canvas.draw()

        # Embed the figure in a Tkinter canvas
        canvas = FigureCanvasTkAgg(fig, master=page)
        canvas.get_tk_widget().config(bg=BACKGROUND_COLOR)
        canvas.get_tk_widget().pack(fill='both', expand=True)

        def on_resize(event):
            width, height = event.width, event.height
            fig.set_size_inches(width / 100, height / 100)  # Adjust size based on DPI
            canvas.draw()

        # Add a label
        label = ctk.CTkLabel(page, text="Chart", font=ctk.CTkFont(size=18))
        label.pack()

        button = ctk.CTkButton(page, text="Update Chart", command=update_plot)
        button.pack(pady=20)
        clear_button = ctk.CTkButton(page, text="Clear Chart", command=clear_chart)
        clear_button.pack(pady=20)
        # test_button = ctk.CTkButton(page, text="test button", command=_test_plot)
        # test_button.pack()

        toolbar = NavigationToolbar2Tk(canvas=canvas, window=page)
        toolbar.config(background=NAVIGATION_BACKGROUND)
        toolbar._message_label.config(background=NAVIGATION_BACKGROUND)
        for button in toolbar.winfo_children():
            button.configure(background=NAVIGATION_BACKGROUND)
        toolbar.pack()

        # Bind the resize event
        page.bind("<Configure>", on_resize)