# Realistic Gearbox for Forza Horizon 4/5

## Introduction

This Python script enhances your driving experience in Forza Horizon 4/5 by simulating a realistic gearbox.
It's perfect for those who enjoy casual driving in the city and occasional quick accelerations for overtaking. Inspired by [a YouTube video](https://www.youtube.com/watch?v=w_d0utwbM1M&ab_channel=TitouanDupuy) on a realistic gearbox, this project aims to bring that experience to everyone.

## Demonstration

Check out the [Demonstration Video](https://youtu.be/d2Cw0pS0UbA) to see the gearbox in action!

## Features

- **Shift like a REAL CAR**: Experience gear shifting just like you would in a real vehicle.
- **Sports Mode**: Hold RPM when intensively driving.
- **Drive Mode Selection**: Choose between Normal, Sports, Eco, or Manual modes.
- **Forza Truck Simulator?**: Trucks are included!

## Installation     [![Github All Releases](https://img.shields.io/github/downloads/GinoLin980/Forza-Horizon-realistic-gearbox/total.svg)]()

### [Release Page](https://github.com/GinoLin980/Forza-Horizon-realistic-gearbox/releases)

- **Standard Users**: Simply download the `.exe` file and run it.
- **Advanced Users**: Download the `.py` file and feel free to tweak the values in your editor.

### **If you installed Forza Horizon from Microsoft Store.**

**Download `FHGearbox_MS_store.exe` and `Ping.and.Retroflect.Utility.exe`.**

## Setup Instructions

- **Requirements**: **A controller or wheel is necessary.**
- **Open Game**: Open up Forza Horizon 4/5
- **Settings**: Ensure gear changing is set to manual and that `Q` and `E` keys can `shift down and up`, respectively.
- **Data Output**: Configure the HUD and gameplay data output as follows:
  - Data Output: `ON`
  - IP Address: `127.0.0.1`
  - Port: `8000`

#### For Microsoft Store Version

1. Run `Ping.and.Retroflect.Utility.exe` and choose a unused IP and ping it to check.(recommend IPs are list in-app)
2. Unused IPs will be listed in the bottom. Choose one and click **Retroflect**.
3. Open up game and set the UDP Data Out IP to `<WHAT YOU CHOSE TO RUN IN RETROFLECT>` and Data Out Port `8000`
4. Open `FHGearbox_MS_store.exe` and have fun!

## Forked From

This project builds upon the work from:

- [Forza Horizon Data Out Python](https://github.com/nikidziuba/Forza_horizon_data_out_python)
- [Assetto Corsa Real Automatic Gearbox](https://github.com/AnnoyingTechnology/assetto-corsa-real-automatic-gearbox)
- [Retroflect](https://github.com/twisteroidambassador/retroflect/)

### Big thanks to these bros, I can't make this without them. 🫶

## Future Goals

- [X] When coasting in high rpm and then full accelerate, it will sometimes upshift first and then downshift(maybe because the code detects too quickly)
- [X] Parameter fine tune(gas_threshold)
- [ ] Add cruise control or pit limiter(I've tried and it's impossible to do without reaching the core of the game, GO [VOTE](https://forums.forza.net/t/realistic-gearbox-in-forza-horizon/703463) TO LET THEM SEE!!!!!!!!!)
- [ ] Add adaptive to slope. Hold RPM and do not upshift when climbing.

## ⚠️DISCLAIMER

This mod might violate the [Forza Code of Conduct](https://support.forzamotorsport.net/hc/en-us/articles/360035563914-Forza-Code-of-Conduct), so take your own responsibility.

**(they are bad at making the game better and they didn't reply my 3 emails and I'm not getting banned yet:) GO [VOTE](https://forums.forza.net/t/realistic-gearbox-in-forza-horizon/703463)**

## Nexus Mod

Find this project on [Nexus Mods.](https://www.nexusmods.com/forzahorizon5/mods/258/?tab=description)

## Support

### Encounter any issues? Post an [Issue](https://github.com/GinoLin980/Forza-Horizon-realistic-gearbox/issues) or join [my Discord server](https://discord.com/invite/Ch9vdu4mT4) to contribute to the development.

### **[Vote on Forza Forum to let us drive towards the horizon](https://forums.forza.net/t/realistic-gearbox-in-forza-horizon/703463)**
