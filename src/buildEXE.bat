cd src
pyinstaller --onefile --icon="utils/car.ico" -w --add-data utils;utils --splash "utils/splash.png" --name="FHGearbox" FH_auto_classes.py
rmdir /s /q "build"
move "dist\FHGearbox.exe" .
rmdir /s /q "dist"
del "FHGearbox.spec"