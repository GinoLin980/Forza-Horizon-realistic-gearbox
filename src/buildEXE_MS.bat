cd src
pyinstaller --onefile --icon="utils/car.ico" -w --add-data utils;utils --splash "utils/splash.png" --name="FHGearbox_MS_store" FH_auto_classes.py
rmdir /s /q "build"
move "dist\FHGearbox_MS_store.exe" .
rmdir /s /q "dist"
del "FHGearbox_MS_store.spec"