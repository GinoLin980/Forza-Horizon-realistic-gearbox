import os, json, webbrowser, requests
import customtkinter as ctk
from PIL import Image

VERSION = "v2"
API_URL = "https://api.github.com/repos/GinoLin980/Forza-Horizon-realistic-gearbox/releases"
REPO_URL = "https://www.github.com/GinoLin980/Forza-Horizon-realistic-gearbox/releases"

started = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

point = '\u2022' # bullet point

Github_logo = ctk.CTkImage(Image.open("Forza-Horizon-realistic-gearbox/utils/github.png"))
YouTube_logo = ctk.CTkImage(Image.open("Forza-Horizon-realistic-gearbox/utils/youtube.png"))
Nexus_logo = ctk.CTkImage(Image.open("Forza-Horizon-realistic-gearbox/utils/nexus.png"))

class UpdateHomeLabels():
    def __init__(self) -> None:
        super().__init__

class CheckUpdate(ctk.CTk):
    def __init__(self):
        response = requests.get(API_URL)
        response.raise_for_status()
        latest_release = response.json()[0]['tag_name']
        need_updated = latest_release != VERSION
        if need_updated:
            super().__init__()
            self.title("NEW VERSION RELEASED!!")
            label = ctk.CTkLabel(self, text=f'A new release is available. Go update!\nCurrent Version: {VERSION}\nLatest Version: {latest_release}')
            label.pack(padx=10, pady=10)
            yes_button = ctk.CTkButton(self, text='Yes', command=lambda: (webbrowser.open_new(REPO_URL), self.destroy()))
            no_button = ctk.CTkButton(self, text='No', command=self.destroy)
            
            yes_button.pack(side='left', padx=20)
            no_button.pack(side='right', padx=20)
            self.mainloop()
            
# a class for changing pages
class PageChange(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
    def show(self):
        self.lift()
        
# class for pages
class Pages(PageChange):
    def __init__(self):
        super().__init__()
        self.page = PageChange()
    
    def Introduction(self):
        page = PageChange()
        page.grid_rowconfigure(0, weight=0)
        page.grid_columnconfigure(0, weight=1)
        
        welcome = ctk.CTkLabel(page, text="Welcome to Forza Horizon Realistic Gearbox", font=ctk.CTkFont(size=25, weight="bold"))
        welcome.grid(padx=10, pady=10, sticky='new', row=0)
        rules = ctk.CTkLabel(page, text=f"\nPlease open up game first\nPlease set the LAST THREE settings in HUD and Gameplay as follows\n{point} 'DATA OUTPUT': ON\n{point} 'IP ADDRESS': 127.0.0.1\n{point} 'PORT': 8000", justify='left', font=ctk.CTkFont(size=15, weight="bold"))
        rules.grid(padx=10, sticky='new', row=1)

        # checkbox to save settings
        def dont_show():
            settings = {"dont_show_intro": dont_show_startup.get()}
            with open('Forza-Horizon-realistic-gearbox/utils/config.json', 'w') as f:
                json.dump(settings, f)
        
        with open('Forza-Horizon-realistic-gearbox/utils/config.json') as f:
            settings = json.load(f)
            toggled = ctk.IntVar(value=1 if settings["dont_show_intro"] else 0)
        
        dont_show_startup = ctk.CTkCheckBox(page, text="Don't show introduction again", variable=toggled, command=dont_show)
        dont_show_startup.grid(padx=10, pady=20, sticky='sew', row=2)
        
        return page

    def HomePage(self, started):
        # Clear the page
        for widget in self.page.winfo_children():
            widget.destroy()

        self.page.grid_rowconfigure(0, weight=0)
        self.page.grid_columnconfigure(0, weight=1)
        
        if started:
            gas_label = ctk.CTkLabel(self.page, text="Gas: 0%", font=ctk.CTkFont(size=20, weight="bold"))
            gas_progress = ctk.CTkProgressBar(self.page, height=30, progress_color="green")
            brake_label = ctk.CTkLabel(self.page, text="Brake: 0%", font=ctk.CTkFont(size=20, weight="bold"))
            brake_progress = ctk.CTkProgressBar(self.page, height=30, width=200, progress_color="red")
            
            gas_label.grid(row=0, pady=10)
            gas_progress.grid(row=1, pady=3)
            brake_label.grid(row=2, pady=8)
            brake_progress.grid(row=3, pady=3)
        else:
            start_button = ctk.CTkButton(self.page, text="Start", command=lambda: self.HomePage(started=True))
            start_button.grid(padx=10, pady=10, row=0) 

        return self.page
    
    def AboutMe(self):
        page = PageChange()
        page.grid_rowconfigure(0, weight=0)
        page.grid_columnconfigure(0, weight=1)
        
        GithubButton = ctk.CTkButton(page, text="My Github", image=Github_logo, command=lambda: webbrowser.open_new("https://github.com/GinoLin980/Forza-Horizon-realistic-gearbox"))
        YouTubeButton = ctk.CTkButton(page, text="My Youtube", image=YouTube_logo, command=lambda: webbrowser.open_new("https://www.youtube.com/channel/UCJJ7gYzhdSZBkOC3NxSjg-A"))
        NexusButton = ctk.CTkButton(page, text="My Nexus", image=Nexus_logo, command=lambda: webbrowser.open_new("https://www.nexusmods.com/forzahorizon5/mods/258/?tab=description"))
        gmail = ctk.CTkLabel(page, text="My Gmail: ppple1872@gmail.com", font=ctk.CTkFont(size=15, weight="bold"))
        
        GithubButton.grid(padx=10, pady=5, row=0, sticky='nw' )
        YouTubeButton.grid(padx=10, pady=5, row=1, sticky='nw')
        NexusButton.grid(padx=10, pady=5, row=2, sticky='nw')
        gmail.grid(padx=10, pady=5, row=3, sticky='nw')
        return page
        
        
# main GUI class
class FHRG_GUI(ctk.CTk):
    def __init__(self, VERSION, condition,  fg_color: str | tuple[str, str] | None = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.condition = condition
        def stopWhile():
            self.condition["stop"] = True
        
        self.title("Forza Horizon Realistic Gearbox")
        self.geometry("800x500")

        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=10)
        

        # Create a container to hold the pages
        container = ctk.CTkFrame(self)
        container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        home = Pages().HomePage(condition["UDP_started"])
        about = Pages().AboutMe()
        intro = Pages().Introduction()
        
        # Add the pages to the container
        intro.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        home.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        about.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        
        # a frame that holds pages' button
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")

        button_frame.grid_rowconfigure(0, weight=0)
        button_frame.grid_rowconfigure(1, weight=0)
        button_frame.grid_rowconfigure(2, weight=0)
        button_frame.grid_rowconfigure(3, weight=1)
        
        intro_button = ctk.CTkButton(button_frame, text="Introduction", fg_color="dim gray", font=ctk.CTkFont(size=14, weight="bold"), command=intro.show)
        intro_button.grid(row=0, column=0, padx=10, pady=5, sticky="new")
        home_button = ctk.CTkButton(button_frame, text="Home", fg_color="dim gray", font=ctk.CTkFont(size=14, weight="bold"), command=home.show)
        home_button.grid(row=1, column=0, padx=10, pady=5, sticky="new")
        about_button = ctk.CTkButton(button_frame, text="About Me", fg_color="dim gray", font=ctk.CTkFont(size=14, weight="bold"), command=about.show)
        about_button.grid(row=2, column=0, padx=10, pady=5, sticky="new")
        quit_button = ctk.CTkButton(button_frame, text="Quit", hover_color="red", command=lambda: (stopWhile(), quit()))
        quit_button.grid(sticky='s')
        
        # Check if the settings file exists and load the settings
        if os.path.exists('Forza-Horizon-realistic-gearbox/utils/config.json'):
            with open('Forza-Horizon-realistic-gearbox/utils/config.json', 'r') as f:
                settings = json.load(f)
        else:
            settings = {'dont_show_intro': False}
            with open('Forza-Horizon-realistic-gearbox/utils/config.json', 'w') as f:
                json.dump(settings, f)


        # If the 'show_intro' setting is False, show the home page
        if settings['dont_show_intro']:
            home.show()
        else:
            intro.show()
            
        CheckUpdate()
        
    

