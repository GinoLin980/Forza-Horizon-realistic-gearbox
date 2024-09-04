import sys; sys.dont_write_bytecode = True
import customtkinter as ctk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from collections import deque
from typing import Deque
import threading

# Constants
BACKGROUND_COLOR = "#242424"
NAVIGATION_BACKGROUND = "#656565"
DYNO_DATA: Deque[dict[str: int|float]] | None = deque([None, None], maxlen=2) # initiate with None



class dyno_frame:
    def __init__(self, page):
        self.page = page
        self.terminate = False

        # Create a figure with a transparent background
        self.fig = Figure(figsize=(5, 3), dpi=100, facecolor='none')
        self.ax = self.fig.add_subplot(facecolor='none')

        # Set spines, ticks, and labels to white
        for spine in self.ax.spines.values():
            spine.set_color('white')

        self.ax.set_xticks(range(0, 3001, 500))
        self.ax.set_yticks(range(0, 601, 100))

        self.ax.tick_params(axis='both', colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

        # Plot an initial blank chart
        self.ax.plot([], [])

        # Embed the figure in a Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=page)
        self.canvas.get_tk_widget().config(bg=BACKGROUND_COLOR)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)


        # Add a label
        label = ctk.CTkLabel(page, text="Chart", font=ctk.CTkFont(size=18))
        label.pack()

        button = ctk.CTkButton(page, text="Update Chart", command=self.update_plot)
        button.pack(pady=3)
        clear_button = ctk.CTkButton(page, text="Clear Chart", command=self.clear_chart)
        clear_button.pack(pady=3)

        test_button = ctk.CTkButton(page, text="Test Plot", command=self._test_plot)
        test_button.pack(pady=3)

        toolbar = NavigationToolbar2Tk(canvas=self.canvas, window=page)
        toolbar.config(background=NAVIGATION_BACKGROUND)
        toolbar._message_label.config(background=NAVIGATION_BACKGROUND)
        for button in toolbar.winfo_children():
            button.configure(background=NAVIGATION_BACKGROUND)
        toolbar.pack()

        # Bind the resize event
        page.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        width, height = event.width, event.height
        self.fig.set_size_inches(width / 100, height / 100)  # Adjust size based on DPI
        self.canvas.draw()

    # Function to update the chart with random curves
    def add_new_power_data(self, data: dict[str: int|float]):
        if None in DYNO_DATA:
            DYNO_DATA.append(data)
            print("DYNO_DATA", DYNO_DATA)
        elif data["rpm"] > DYNO_DATA[-1]["rpm"]:
            DYNO_DATA.append(data)
            self.update_plot()

    def update_plot(self):
        # self.ax.clear()
        rpms = deque([d['rpm'] for d in DYNO_DATA], maxlen=2)
        hps = deque([d['hp'] for d in DYNO_DATA], maxlen=2)
        torques = deque([d['torque'] for d in DYNO_DATA], maxlen=2)
        self.ax.plot(rpms, hps, color='red', label='Horsepower')
        self.ax.plot(rpms, torques, color='blue', label='Torque')
        
        self.ax.tick_params(axis='both', colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        
        # self.ax.legend(loc='upper left', facecolor=BACKGROUND_COLOR, labelcolor='white')
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def clear_chart(self):
        self.ax.clear()
        self.ax.set_xticks(range(0, 3001, 500))
        self.ax.set_yticks(range(0, 601, 100))
        self.canvas.draw()
        DYNO_DATA.extend([None, None])
        self.terminate = True

    def _test_plot(self):
            # Initialize DYNO_DATA with some starting values
            DYNO_DATA.clear()
            DYNO_DATA.extend([{'rpm': 1000, 'hp': 100, 'torque': 200},
                            {'rpm': 1500, 'hp': 120, 'torque': 250}])
            x_ax = list(range(0, 3001, 1000))
            y_ax = list(range(0, 601, 100))

            # Extract initial data
            rpms = deque([d['rpm'] for d in DYNO_DATA], maxlen=2)
            hps = deque([d['hp'] for d in DYNO_DATA], maxlen=2)
            torques = deque([d['torque'] for d in DYNO_DATA], maxlen=2)

            # Create plot lines
            hp_line, = self.ax.plot(rpms, hps, color='red', label='Horsepower')
            torque_line, = self.ax.plot(rpms, torques, color='blue', label='Torque')
            self.ax.legend(loc='upper left', facecolor=BACKGROUND_COLOR, labelcolor='white')

            # Update function for animation
            def update(i):
                # Update data
                new_rpm = rpms[-1] * 1.0005
                new_hp = hps[-1] * 1.0005
                new_torque = torques[-1] * 1.0005
                
                rpms.append(new_rpm)
                hps.append(new_hp)
                torques.append(new_torque)

                x_ax.append(x_ax[-1] + 1000) if  rpms[-1] > x_ax[-1] else None
                y_ax.append(y_ax[-1] + 100) if  max(hps[-1], torques[-1]) > y_ax[-1] else None

                self.ax.tick_params(axis='both', colors='white', labelsize=8)
                self.ax.set_xticks(x_ax)
                self.ax.set_yticks(y_ax)

                # # Update plot lines
                # hp_line.set_data(rpms, hps)
                # torque_line.set_data(rpms, torques)

                self.ax.plot(rpms, hps, color='red', label='Horsepower')
                self.ax.plot(rpms, torques, color='blue', label='Torque')
                
                self.ax.relim()
                self.ax.autoscale_view()

            # # Use FuncAnimation to update the plot
            # from matplotlib.animation import FuncAnimation
            # ani = FuncAnimation(self.fig, update, frames=range(8000), repeat=False, interval=50)

            for i in range(3000):
                update(i)
                self.page.update()
                # Draw the canvas
                self.canvas.draw()
                if self.terminate:
                    self.terminate = False
                    break