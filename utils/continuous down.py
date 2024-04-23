# this script will make a data for jumping gears only
import keyboard

if keyboard.is_pressed('space'):
    for i in range(3):
        keyboard.press('q')