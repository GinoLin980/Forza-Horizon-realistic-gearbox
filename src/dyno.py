import sys; sys.dont_write_bytecode = True
import customtkinter as ctk
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from collections import deque
from typing import Deque
import time

# Constants
BACKGROUND_COLOR = "#242424"
NAVIGATION_BACKGROUND = "#656565"
DYNO_DATA: Deque[dict[str, int|float] | None] = deque([None, None], maxlen=2) # initiate with None



class dyno_frame:
    def __init__(self, page):
        self.page = page
        self.terminate = False

        self.last_update_time = 0
        self.update_interval = 0.005

        self.line_hp = None
        self.line_torque = None
        self.background = None

        self.max_hp = 0
        self.max_torque = 0
        self.max_hp_rpm = 0
        self.max_torque_rpm = 0

        self.update_interval = 0.004 # 10ms

        # Create a figure with a transparent background
        self.fig = Figure(figsize=(5, 3), dpi=100, facecolor='none')
        self.ax = self.fig.add_subplot(facecolor='none')

        # Set spines, ticks, and labels to white
        for spine in self.ax.spines.values():
            spine.set_color('white')

        self.x_ax = list(range(0, 3001, 1000))
        self.y_ax = list(range(0, 101, 100))

        self.ax.set_xticks(self.x_ax)
        self.ax.set_yticks(self.y_ax)

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
        self.max_label = ctk.CTkLabel(page, text="Max HP: None\nMax Torque: None", font=ctk.CTkFont(size=18))
        self.max_label.pack()

        button_frame = ctk.CTkFrame(page)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        clear_button = ctk.CTkButton(button_frame, text="Clear Chart", command=self.clear_chart)
        clear_button.grid(row=0, column=0, padx=30, pady=30)

        save_button = ctk.CTkButton(button_frame, text="Save Chart", command=self.save_dyno)
        save_button.grid(row=0, column=1, padx=30, pady=30)

        button_frame.pack(fill='both')

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
    def add_new_power_data(self, data: dict[str, int|float]):
        if self.terminate:
            self.terminate = False
        if None in DYNO_DATA or data["rpm"] > DYNO_DATA[-1]["rpm"]:
            DYNO_DATA.append(data)
            if data["hp"] > self.max_hp:
                self.max_hp = data["hp"]
                self.max_hp_rpm = data["rpm"]
            if data["torque"] > self.max_torque:
                self.max_torque = data["torque"]
                self.max_torque_rpm = data["rpm"]
            if not None in DYNO_DATA:
                self.update_plot()

    def after_plot(self):
        hp_patch = mpatches.Patch(color='red', label='Horsepower')
        torque_patch = mpatches.Patch(color='blue', label='Torque')
        self.ax.legend(handles=[hp_patch, torque_patch], loc='lower right', facecolor=BACKGROUND_COLOR, labelcolor='white')
        self.y_ax.append(max(self.max_hp, self.max_torque) * 1.2) if max(self.max_hp, self.max_torque) * 1.2 > self.y_ax[-1] else lambda: ...
        if self.y_ax[-1] > 2800:
            self.y_ax = [self.y_ax[-1]] + [ y for y in self.y_ax if y % 500 == 0]
        elif self.y_ax[-1] > 1200:
            self.y_ax = [self.y_ax[-1]] + [y for y in self.y_ax if y % 200 == 0]
        self.ax.set_yticks(self.y_ax)
        self.ax.relim()
        self.max_label.configure(text=f"Max HP: {self.max_hp:.2f} @ {self.max_hp_rpm} rpm\nMax Torque: {self.max_torque:.2f} @ {self.max_torque_rpm} rpm")
        # self.ax.annotate(f"{self.max_hp:.2f} @ {self.max_hp_rpm} rpm", color='white', xy=(self.max_hp_rpm, self.max_hp), xytext=(-70, 10), textcoords='offset points', arrowprops=dict(facecolor="white", arrowstyle='->', connectionstyle='arc3,rad=0'))
        # self.ax.annotate(f"{self.max_torque:.2f} @ {self.max_torque_rpm} rpm", color='white', xy=(self.max_torque_rpm, self.max_torque), xytext=(-120, -15), textcoords='offset points', arrowprops=dict(facecolor="white", arrowstyle='->', connectionstyle='arc3, rad=0'))
        self.canvas.draw()
        

    def save_dyno(self):
        file_path = ctk.filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")], initialfile="FHRG_dyno.png")
        if file_path:
            self.fig.savefig(file_path)

    def update_plot(self):
        if None in DYNO_DATA or len(DYNO_DATA) < 2:
            return
        if time.time() - self.last_update_time < self.update_interval:
            return

        rpms = [d['rpm'] for d in DYNO_DATA if d is not None]
        hps = [d['hp'] for d in DYNO_DATA if d is not None]
        torques = [d['torque'] for d in DYNO_DATA if d is not None]

        if self.background is None:
            if rpms[-1] > self.x_ax[-1]:
                self.x_ax.append(self.x_ax[-1] + 1000)
            if max(hps[-1], torques[-1]) > self.y_ax[-1]:
                self.y_ax.append(self.y_ax[-1] + 100)
            self.ax.set_xticks(self.x_ax)
            self.ax.set_yticks(self.y_ax)
            self.ax.tick_params(axis='both', colors='white', labelsize=8)
            self.ax.xaxis.label.set_color('white')
            self.ax.yaxis.label.set_color('white')
            self.ax.title.set_color('white')
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)

        if rpms[-1] > self.x_ax[-1]:
            self.x_ax.append(self.x_ax[-1] + 1000)
        if max(hps[-1], torques[-1]) > self.y_ax[-1]:
            self.y_ax.append(self.y_ax[-1] + 100)
        self.ax.set_xticks(self.x_ax)
        self.ax.set_yticks(self.y_ax)
        self.ax.relim()
        self.ax.autoscale_view()

        # Update the background image after changing axis limits
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)

        self.line_hp, = self.ax.plot(rpms, hps, color='red', label='Horsepower')
        self.line_torque, = self.ax.plot(rpms, torques, color='blue', label='Torque')

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.line_hp)
        self.ax.draw_artist(self.line_torque)
        self.canvas.blit(self.ax.bbox)
        self.canvas.flush_events()
        self.last_update_time = time.time()

    def clear_chart(self):
        self.max_hp = 0
        self.max_torque = 0
        self.max_hp_rpm = 0
        self.max_torque_rpm = 0

        self.ax.clear()
        self.x_ax = list(range(0, 3001, 1000))
        self.y_ax = list(range(0, 101, 100))

        self.ax.set_xticks(self.x_ax)
        self.ax.set_yticks(self.y_ax)
        self.canvas.draw()
        DYNO_DATA.extend([None, None])
        self.terminate = True

    def _test_plot(self):
            # Initialize DYNO_DATA with some starting values
            DYNO_DATA.clear()
            DYNO_DATA.extend([{'rpm': 1000, 'hp': 100, 'torque': 200},
                            {'rpm': 1500, 'hp': 120, 'torque': 250}])
            x_ax = list(range(0, 3001, 1000))
            y_ax = list(range(0, 101, 100))

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