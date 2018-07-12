# Scooter lights

## lightbuttonprogram.py
Crude python program that
- Creates light patterns on APA102 pixels attached to Raspberry PI SPI outputs (via bibliopixel library)
- Intercepts GPIO button input and plays WAV audio file 

## scooter.sh
Loads and runs lightbuttonprogram.py continuously as a deamon
