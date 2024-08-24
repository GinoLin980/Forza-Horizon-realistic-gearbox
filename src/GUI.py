import sys
import os
import json
import threading
import webbrowser
import requests
from typing import Dict, Union
from PIL import Image, ImageTk
import customtkinter as ctk
from dyno import *

# Constants
API_URL = (
    "https://api.github.com/repos/GinoLin980/Forza-Horizon-realistic-gearbox/releases"
)
REPO_URL = "https://www.github.com/GinoLin980/Forza-Horizon-realistic-gearbox/releases"
POINT = "\u2022"  # bullet point

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# Utility function to return absolute path
def image_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Load images
Github_logo = ctk.CTkImage(Image.open(image_path("utils/github.png")))
YouTube_logo = ctk.CTkImage(Image.open(image_path("utils/youtube.png")))
Nexus_logo = ctk.CTkImage(Image.open(image_path("utils/nexus.png")))
Forza_logo = ctk.CTkImage(Image.open(image_path("utils/forza.png")))


# For "X" on the top right of the window
def do_nothing() -> None:
    pass


# Class for changing pages
class PageChange(ctk.CTkFrame):
    """Base class for lifting pages"""

    def __init__(self, master=None) -> None:
        super().__init__(master)

    def show(self) -> None:
        self.lift()


# Class for pages
class Pages(PageChange):
    def __init__(self) -> None:
        super().__init__()
        self.page = PageChange()

    def Introduction(self) -> PageChange:
        page = PageChange()
        page.grid_rowconfigure(0, weight=0)
        page.grid_columnconfigure(0, weight=1)

        welcome = ctk.CTkLabel(
            page,
            text="Welcome to Forza Horizon Realistic Gearbox",
            font=ctk.CTkFont(size=25, weight="bold"),
        )
        rules = ctk.CTkLabel(
            page,
            text=(
                "\nPlease open up game first\n"
                "Make sure that up/down shift are bound to Q/E\n"
                "Please set the LAST THREE settings in HUD and Gameplay as follows\n"
                f"{POINT} 'DATA OUTPUT': ON\n"
                f"{POINT} 'IP ADDRESS': 127.0.0.1\n"
                f"{POINT} 'PORT': 8000\n"
                "And change the driving mode by clicking\n"
                f"{POINT}7: Comfort\n"
                f"{POINT}8: Sports\n"
                f"{POINT}9: Eco\n"
                f"{POINT}0: Manual"
            ),
            justify="left",
            font=ctk.CTkFont(size=15, weight="bold"),
        )

        welcome.grid(padx=10, pady=10, sticky="new", row=0)
        rules.grid(padx=10, sticky="new", row=1)

        # Checkbox to save settings
        def dont_show():
            settings = {"dont_show_intro": dont_show_startup.get()}
            with open(image_path("utils/config.json"), "w") as f:
                json.dump(settings, f)

        with open(image_path("utils/config.json")) as f:
            settings = json.load(f)

        toggled = ctk.IntVar(value=1 if settings["dont_show_intro"] else 0)
        dont_show_startup = ctk.CTkCheckBox(
            page,
            text="Don't show introduction again",
            variable=toggled,
            command=dont_show,
        )
        dont_show_startup.grid(padx=10, pady=20, sticky="sew", row=2)
        return page

    def AboutMe(self, VERSION) -> PageChange:
        page = PageChange()
        page.grid_rowconfigure(0, weight=0)
        page.grid_columnconfigure(0, weight=1)

        GithubButton = ctk.CTkButton(
            page,
            text="My Github",
            image=Github_logo,
            command=lambda: webbrowser.open_new("https://github.com/GinoLin980"),
        )
        YouTubeButton = ctk.CTkButton(
            page,
            text="My Youtube",
            image=YouTube_logo,
            command=lambda: webbrowser.open_new(
                "https://www.youtube.com/channel/UCJJ7gYzhdSZBkOC3NxSjg-A"
            ),
        )
        NexusButton = ctk.CTkButton(
            page,
            text="My Nexus",
            image=Nexus_logo,
            command=lambda: webbrowser.open_new(
                "https://www.nexusmods.com/forzahorizon5/mods/258/?tab=description"
            ),
        )
        gmail = ctk.CTkLabel(
            page,
            text="My Gmail: ppple1872@gmail.com",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        VoteButton = ctk.CTkButton(
            page,
            text="Vote On Forza Community !!!",
            image=Forza_logo,
            hover_color="hot pink",
            command=lambda: webbrowser.open(
                "https://forums.forza.net/t/realistic-gearbox-in-forza-horizon/703463"
            ),
            font=ctk.CTkFont(weight="bold"),
            fg_color="red",
        )
        VersionLabel = ctk.CTkLabel(
            page,
            text=f"Current Version: {VERSION}",
            font=ctk.CTkFont(size=20, weight="bold"),
        )

        VoteButton.grid(padx=10, pady=20, row=1, sticky="new")
        GithubButton.grid(padx=10, pady=5, row=3, sticky="nw")
        YouTubeButton.grid(padx=10, pady=5, row=4, sticky="nw")
        NexusButton.grid(padx=10, pady=5, row=5, sticky="nw")
        gmail.grid(padx=10, pady=5, row=6, sticky="nw")

        page.grid_rowconfigure(7, weight=10)
        VersionLabel.grid(padx=20, pady=20, row=7, sticky="se")

        return page

    def HomePage(self, started: bool) -> PageChange:
        self.page = PageChange()
        for widget in self.page.winfo_children():
            widget.destroy()

        self.page.grid_rowconfigure(0, weight=0)
        self.page.grid_columnconfigure(0, weight=1)

        if started:
            self.gas_label = ctk.CTkLabel(
                self.page, text="Gas: 0%", font=ctk.CTkFont(size=20, weight="bold")
            )
            self.gas_progress = ctk.CTkProgressBar(
                self.page, height=30, progress_color="green"
            )
            self.brake_label = ctk.CTkLabel(
                self.page, text="Brake: 0%", font=ctk.CTkFont(size=20, weight="bold")
            )
            self.brake_progress = ctk.CTkProgressBar(
                self.page, height=30, width=200, progress_color="red"
            )
            self.gear_label = ctk.CTkLabel(
                self.page, text="D1", font=ctk.CTkFont(size=20, weight="bold")
            )
            drive_mode_label = ctk.CTkLabel(
                self.page,
                text=(
                    f"Change the driving mode by clicking\n"
                    f"{POINT}7: Comfort\n"
                    f"{POINT}8: Sports\n"
                    f"{POINT}9: Eco\n"
                    f"{POINT}0: Manual"
                ),
                justify="left",
                font=ctk.CTkFont(size=20, weight="bold"),
            )

            self.gas_label.grid(row=0, pady=10)
            self.gas_progress.grid(row=1, pady=3)
            self.brake_label.grid(row=2, pady=8)
            self.brake_progress.grid(row=3, pady=3)
            self.gear_label.grid(row=4, pady=10)
            drive_mode_label.grid(row=5, pady=10)
        else:
            error_label = ctk.CTkLabel(
                self.page,
                text=(
                    "THE UDP SERVER ISN'T RECEIVING ANY DATA\n"
                    "PLEASE MAKE SURE THAT YOU'VE SET UP THE SETTINGS CORRECTLY\n\n"
                    "OTHERWISE, FOLLOW THE INSTRUCTION ON MY GITHUB REPO \nTO USE Retroflect TO SOLVE."
                ),
                text_color="red",
                font=ctk.CTkFont(size=15, weight="bold"),
            )
            error_label.grid(padx=20, pady=20)
            error_repo_button = ctk.CTkButton(self.page, text="My Repository", command=lambda: webbrowser.open_new("https://www.github.com/GinoLin980/Forza-Horizon-realistic-gearbox"))
            error_repo_button.grid(padx=20, pady=20)

        return self.page

    def update_data(self, gas: float, brake: float, gear: int, drive_mode: str):
        self.gas_label.configure(text=f"Gas: {int(gas * 100)}%")
        self.brake_label.configure(text=f"Brake: {int(brake * 100)}%")
        self.gas_progress.set(gas)
        self.brake_progress.set(brake)

        match drive_mode:
            case "S":
                gear_color = "red"
            case "D":
                gear_color = "blue"
            case "E":
                gear_color = "green"
            case "M":
                gear_color = "white"

        self.gear_label.configure(
            text=f"{drive_mode}{gear}" if gear != 0 else "R",
            text_color=gear_color
        )  

    def Dyno(self):
        self.page = PageChange()
        self.dyno = dyno_frame(self.page)
        return self.page


# Main GUI class
class FHRG_GUI(ctk.CTk):
    def __init__(
        self,
        VERSION: str,
        condition: Dict[str, Union[bool, int, str]],
        fg_color: str | tuple[str, str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(fg_color, **kwargs)
        self.VERSION = VERSION
        self.condition = condition

        self.iconbitmap(image_path("utils/car.ico"))
        self.title("Forza Horizon Realistic Gearbox")
        self.geometry("800x500")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=10)

        self.check_update()

        # Create a container to hold the pages
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        page_instance = Pages()
        self.home = page_instance.HomePage(condition["UDP_started"])
        about = page_instance.AboutMe(self.VERSION)
        self.intro = page_instance.Introduction()
        self.dyno = page_instance.Dyno()
        self.dyno.dy

        # Add the pages to the self.container
        self.intro.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.home.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.dyno.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        about.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        # A frame that holds pages' button
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")
        self.button_frame.grid_rowconfigure(0, weight=0)
        self.button_frame.grid_rowconfigure(3, weight=1)
        self.button_frame.grid_rowconfigure(4, weight=0)

        intro_button = ctk.CTkButton(
            self.button_frame,
            text="Introduction",
            fg_color="dim gray",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.intro.show,
        )
        intro_button.grid(row=0, column=0, padx=10, pady=5, sticky="new")

        self.home_button = ctk.CTkButton(
            self.button_frame,
            text="Home",
            fg_color="dim gray",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.home.show,
        )
        self.home_button.grid(row=1, column=0, padx=10, pady=5, sticky="new")

        self.dyno_button = ctk.CTkButton(
            self.button_frame,
            text="Dyno",
            fg_color="dim gray",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.dyno.show,
        )
        self.dyno_button.grid(row=2, column=0, padx=10, pady=5, sticky="new")

        about_button = ctk.CTkButton(
            self.button_frame,
            text="About Me",
            fg_color="dim gray",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=about.show,
        )
        about_button.grid(row=3, column=0, padx=10, pady=5, sticky="new")

        always_on_top = ctk.CTkCheckBox(
            self.button_frame,
            text="Always on top",
            command=lambda: self.attributes(
                "-topmost", True if always_on_top.get() else False
            ),
        )
        always_on_top.grid(padx=10, sticky="sew")

        vote_here_button = ctk.CTkButton(
            self.button_frame,
            text="Vote Here",
            text_color="black",
            fg_color="PeachPuff2",
            hover_color="PeachPuff3",
            command=lambda: (
                webbrowser.open(
                    "https://forums.forza.net/t/realistic-gearbox-in-forza-horizon/703463"
                )
            ),
        )
        vote_here_button.grid(padx=15, pady=10, sticky="sew")

        quit_button = ctk.CTkButton(
            self.button_frame,
            text="Quit",
            hover_color="red",
            command=lambda: (self.stopWhile(), sys.exit()),
        )
        quit_button.grid(sticky="s")

        # Check if the settings file exists and load the settings
        if os.path.exists(image_path("utils/config.json")):
            with open(image_path("utils/config.json"), "r") as f:
                self.settings = json.load(f)
        else:
            self.settings = {"dont_show_intro": False}
            with open(image_path("utils/config.json"), "w") as f:
                json.dump(self.settings, f)

        # If the 'show_intro' setting is False, show the home page
        if self.settings["dont_show_intro"]:
            self.home.show()
        else:
            self.intro.show()

        self.UDP_started(condition)
        self.update_home = self.update_home_function
        self.protocol("WM_DELETE_WINDOW", do_nothing)

    def update_home_function(self, condition):
        Pages.update_data(
            self,
            gas=condition["gas"],
            brake=condition["brake"],
            drive_mode=condition["drive_mode"],
            gear=condition["gear"],
        )

    def UDP_started(self, condition: Dict[str, Union[bool, int, str]]):
        if condition["UDP_started"]:
            self.home = Pages.HomePage(self, started=True)
            self.home.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
            if not self.settings["dont_show_intro"]:
                self.intro.show
            self.home_button = ctk.CTkButton(
                self.button_frame,
                text="Home",
                fg_color="dim gray",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self.home.show,
            )
            self.home_button.grid(row=1, column=0, padx=10, pady=5, sticky="new")

    def check_update(self):
        def on_yes():
            webbrowser.open_new_tab(REPO_URL)
            update_window.quit()
            update_window.destroy()

        # Function to handle the "No" button click
        def on_no():
            update_window.quit()
            update_window.destroy()
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            latest_release = response.json()[0]["tag_name"]
            release_note = response.json()[0]["body"]

            try:
                release_note = release_note.split("Release Note:\n")[1]
                release_note = release_note.replace("* ", "")
            except:
                release_note = "No release note provided"
            need_updated = latest_release != self.VERSION
            if need_updated:
                update_window = ctk.CTk()
                update_window.title("NEW VERSION RELEASED!!")
                label = ctk.CTkLabel(
                    update_window,
                    text=(
                        f"A new release is available. Go update!\n"
                        f"Current Version: {self.VERSION}\n"
                        f"Latest Version: {latest_release}"
                    ),
                )
                label.pack(padx=10, pady=10)

                ### Easter Egg
                latest_release_comp = int(latest_release[1:].replace(".", ""))
                current_version_comp = int(self.VERSION[1:].replace(".", ""))
                if latest_release_comp < current_version_comp:
                    Egg = ctk.CTkLabel(
                        update_window,
                        text="YOU SUS\nARE YOU A DEVELOPER?\nWHY NOT JOIN MY DEVELOPMENT :)",
                        font=ctk.CTkFont(size=20, weight="bold"),
                        text_color="light pink",
                    )
                    Egg.pack(padx=10, pady=20)
                ###

                log = ctk.CTkLabel(
                    update_window, text="Changelog:\n" + release_note, justify="left"
                )
                log.pack(padx=10, pady=10)
                yes_button = ctk.CTkButton(
                    update_window,
                    text="Yes",
                    command=on_yes
                )
                no_button = ctk.CTkButton(
                    update_window,
                    text="No",
                    command=on_no
                )
                yes_button.pack(side="left", padx=20)
                no_button.pack(side="right", padx=20)
                update_window.protocol("WM_DELETE_WINDOW", on_no)
                update_window.mainloop()
        except:
            pass

    # Function to stop the while loop
    def stopWhile(self):
        self.condition["stop"] = True


# Run this file to directly check the functionality. (showcase mode)
if __name__ == "__main__":
    ## FAKE DATA
    condition = {}
    condition["UDP_started"] = False
    condition["gas"] = 0
    condition["brake"] = 0
    condition["gear"] = 0
    condition["drive_mode"] = "D"
    condition["stop"] = False
    ## FAKE DATA
    APP = FHRG_GUI("v2.3.3", condition)
    while True:
        APP.update()
        if condition["stop"]:
                sys.exit()
